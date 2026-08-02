import hashlib
import importlib.util
import os
from pathlib import Path
import runpy
import sys

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "build_legacy_release.py"
SPEC = importlib.util.spec_from_file_location("build_legacy_release", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def test_release_spec_does_not_rewrite_executable_resources():
    assert builder.SPEC_TEMPLATE.count("icon=None") == 2
    assert "icon={" not in builder.SPEC_TEMPLATE


def test_release_includes_complete_openal_runtime():
    assert "ALURE32.dll" in builder.EXTRA_RUNTIME_FILES
    assert "OpenAL32.dll" in builder.EXTRA_RUNTIME_FILES


def test_release_spec_installs_unicode_bootstrap_before_tk_runtime_hook():
    assert "runtime_hooks=[{runtime_hook!r}]" in builder.SPEC_TEMPLATE
    assert builder.UNICODE_BOOTSTRAP_HOOK.is_file()


def test_unicode_bootstrap_uses_the_ascii_runtime_prefix(monkeypatch, tmp_path):
    runtime = tmp_path / "SHORT"
    (runtime / "tcl").mkdir(parents=True)
    (runtime / "tk").mkdir()
    broken_path = r"C:\Games\????_???\runtime"
    original_path = list(sys.path)

    monkeypatch.setattr(sys, "prefix", str(runtime))
    monkeypatch.setattr(sys, "exec_prefix", str(runtime))
    monkeypatch.setattr(sys, "_MEIPASS", broken_path, raising=False)
    monkeypatch.setattr(sys, "path", [broken_path] + original_path)
    for name in ("TCL_LIBRARY", "TK_LIBRARY", "TIX_LIBRARY"):
        monkeypatch.delenv(name, raising=False)

    runpy.run_path(str(builder.UNICODE_BOOTSTRAP_HOOK))

    assert sys._MEIPASS == str(runtime)
    assert sys.prefix == str(runtime)
    assert sys.exec_prefix == str(runtime)
    assert sys.path[0] == str(runtime)
    assert os.environ["TCL_LIBRARY"] == str(runtime / "tcl")
    assert os.environ["TK_LIBRARY"] == str(runtime / "tk")
    assert os.environ["TIX_LIBRARY"] == str(runtime / "tcl")


def test_restore_clean_bootloader_requires_and_copies_pinned_bytes(
    monkeypatch, tmp_path
):
    payload = b"pristine PyInstaller windowed bootloader"
    source = tmp_path / "runw.exe"
    source.write_bytes(payload)
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "aos.exe").write_bytes(b"resource-mutated executable")

    monkeypatch.setattr(builder, "CLEAN_WINDOWED_BOOTLOADER", source)
    monkeypatch.setattr(builder, "CLEAN_WINDOWED_BOOTLOADER_SHA256", digest(payload))
    builder.restore_clean_windowed_bootloader(runtime)

    assert (runtime / "aos.exe").read_bytes() == payload


def test_restore_clean_bootloader_rejects_unpinned_bytes(monkeypatch, tmp_path):
    source = tmp_path / "runw.exe"
    source.write_bytes(b"unexpected bootloader")
    runtime = tmp_path / "runtime"
    runtime.mkdir()

    monkeypatch.setattr(builder, "CLEAN_WINDOWED_BOOTLOADER", source)
    monkeypatch.setattr(builder, "CLEAN_WINDOWED_BOOTLOADER_SHA256", "0" * 64)
    with pytest.raises(RuntimeError, match="pinned SHA-256"):
        builder.restore_clean_windowed_bootloader(runtime)


def fake_download(url, destination):
    """Stand in for download_file, which creates the parent directory itself."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(b"payload")


def test_every_toolchain_component_pins_a_sha256():
    unpinned = [
        component["name"]
        for component in builder.TOOLCHAIN_COMPONENTS
        if not component.get("sha256")
    ]
    assert unpinned == []


def test_toolchain_component_without_sha256_is_rejected(monkeypatch, tmp_path):
    component = {
        "name": "unpinned-1.0",
        "archive": "unpinned-1.0.tar.gz",
        "url": "https://example.invalid/unpinned-1.0.tar.gz",
    }
    monkeypatch.setattr(builder, "TOOLCHAIN_VENDOR", tmp_path / "vendor")
    monkeypatch.setattr(builder, "TOOLCHAIN_DOWNLOADS", tmp_path / "downloads")
    monkeypatch.setattr(builder, "download_file", fake_download)

    with pytest.raises(RuntimeError, match="no pinned sha256"):
        builder.ensure_toolchain_component(component)


def test_toolchain_component_with_wrong_sha256_is_rejected(monkeypatch, tmp_path):
    component = {
        "name": "tampered-1.0",
        "archive": "tampered-1.0.tar.gz",
        "url": "https://example.invalid/tampered-1.0.tar.gz",
        "sha256": "0" * 64,
    }
    monkeypatch.setattr(builder, "TOOLCHAIN_VENDOR", tmp_path / "vendor")
    monkeypatch.setattr(builder, "TOOLCHAIN_DOWNLOADS", tmp_path / "downloads")
    monkeypatch.setattr(builder, "download_file", fake_download)

    with pytest.raises(RuntimeError, match="failed SHA-256 verification"):
        builder.ensure_toolchain_component(component)
    # A rejected archive must not be left behind, or the early-return in
    # download_file would treat the tampered copy as already fetched.
    assert not (tmp_path / "downloads" / "tampered-1.0.tar.gz").exists()


def test_build_rejects_a_64_bit_interpreter(monkeypatch, tmp_path):
    calls = []

    class Probe:
        stdout = "64\n"

    def fake_run(command, **kwargs):
        calls.append(command)
        return Probe()

    monkeypatch.setattr(builder, "PY2_PYTHON", tmp_path / "python.exe")
    monkeypatch.setattr(builder.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="32-bit"):
        builder.assert_build_interpreter_is_32bit()
    assert calls, "the interpreter should actually be probed"


def test_build_accepts_a_32_bit_interpreter(monkeypatch, tmp_path):
    class Probe:
        stdout = "32\n"

    monkeypatch.setattr(builder, "PY2_PYTHON", tmp_path / "python.exe")
    monkeypatch.setattr(builder.subprocess, "run", lambda command, **kwargs: Probe())

    builder.assert_build_interpreter_is_32bit()


def test_copy_assets_names_a_missing_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(builder, "ROOT", tmp_path)
    monkeypatch.setattr(builder, "ASSET_DIRECTORIES", ["png"])

    with pytest.raises(RuntimeError, match="asset directory is missing"):
        builder.copy_assets(tmp_path / "stage")


def test_download_retries_then_succeeds(monkeypatch, tmp_path):
    attempts = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, *args):
            return b""

    def flaky_urlopen(url, timeout=None):
        attempts.append(timeout)
        if len(attempts) < 2:
            raise OSError("connection reset")
        return Response()

    monkeypatch.setattr(builder.urllib.request, "urlopen", flaky_urlopen)
    monkeypatch.setattr(builder.shutil, "copyfileobj", lambda source, handle: handle.write(b"ok"))

    destination = tmp_path / "archive.tar.gz"
    builder.download_file("https://example.invalid/archive.tar.gz", destination)

    assert destination.read_bytes() == b"ok"
    assert len(attempts) == 2
    assert all(timeout is not None for timeout in attempts), "every request must set a timeout"
    assert not (tmp_path / "archive.tar.gz.partial").exists()


def test_download_gives_up_and_leaves_no_partial_file(monkeypatch, tmp_path):
    def always_fails(url, timeout=None):
        raise OSError("connection reset")

    monkeypatch.setattr(builder.urllib.request, "urlopen", always_fails)

    destination = tmp_path / "archive.tar.gz"
    with pytest.raises(RuntimeError, match="after 3 attempts"):
        builder.download_file("https://example.invalid/archive.tar.gz", destination)

    assert not destination.exists()
    assert not (tmp_path / "archive.tar.gz.partial").exists()


def test_release_spec_disables_upx_compression():
    assert "upx=True" not in builder.SPEC_TEMPLATE
    assert builder.SPEC_TEMPLATE.count("upx=False") == 3


def test_version_argument_must_match_source_marker(monkeypatch, tmp_path):
    marker = tmp_path / "VERSION"
    marker.write_text("0.1.3\n", encoding="ascii")
    monkeypatch.setattr(builder, "SOURCE_VERSION_FILE", marker)

    builder.validate_release_version("0.1.3")
    with pytest.raises(RuntimeError, match="does not match"):
        builder.validate_release_version("0.1.2")


def test_checksum_manifest_covers_each_artifact(monkeypatch, tmp_path):
    first = tmp_path / "client.zip"
    second = tmp_path / "client.7z"
    first.write_bytes(b"zip")
    second.write_bytes(b"seven zip")
    monkeypatch.setattr(builder, "ARTIFACTS_ROOT", tmp_path)

    checksum_path = builder.write_artifact_checksums("0.1.3", [first, second])
    lines = checksum_path.read_text(encoding="ascii").splitlines()

    assert lines == [
        "%s  client.7z" % digest(b"seven zip"),
        "%s  client.zip" % digest(b"zip"),
    ]
