"""Tests for the native module routing shim.

These deliberately avoid the real `.pyd` files: the shim has to be verifiable
on macOS and Linux, where those modules cannot be loaded at all.
"""

import sys
import types
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from port import native_modules


@pytest.fixture(autouse=True)
def clean_meta_path():
    """Never leave a finder installed; it would leak into other test modules."""
    yield
    native_modules.uninstall()


@pytest.fixture
def stub_parent_packages(monkeypatch):
    """Stand in for the `aoslib` and `shared` packages.

    Importing `shared.glm` imports the `shared` package first, and its
    `__init__` does `import shared.bytes, shared.packet` - both native modules
    that do not exist off Windows. The shim routes a leaf module; it cannot
    rescue a parent package whose own import fails, so the parents are replaced
    here with empty stand-ins to isolate what is being tested.
    """
    for name in ("aoslib", "shared"):
        package = types.ModuleType(name)
        package.__path__ = []
        monkeypatch.setitem(sys.modules, name, package)


def test_default_routing_leaves_every_module_on_the_original():
    summary = native_modules.status({})
    assert summary[native_modules.ORIGINAL] == list(native_modules.NATIVE_MODULES)
    assert summary[native_modules.REPLACEMENT] == []
    assert summary[native_modules.STUB] == []


def test_installing_without_routes_does_not_intercept_anything():
    finder = native_modules.install({})
    # Returning None from both hooks is what defers to the normal import
    # machinery, which is what keeps the client unaffected.
    assert finder.find_module("aoslib.world") is None
    assert finder.find_spec("aoslib.world") is None


def test_uninstall_removes_the_finder():
    native_modules.install({})
    assert any(isinstance(f, native_modules.NativeModuleFinder) for f in sys.meta_path)
    native_modules.uninstall()
    assert not any(isinstance(f, native_modules.NativeModuleFinder) for f in sys.meta_path)


def test_install_replaces_a_previously_installed_finder():
    native_modules.install({})
    native_modules.install({})
    installed = [f for f in sys.meta_path if isinstance(f, native_modules.NativeModuleFinder)]
    assert len(installed) == 1


def test_stub_backend_refuses_the_import_and_names_the_module(stub_parent_packages):
    native_modules.install({"aoslib.world": native_modules.STUB})
    with pytest.raises(ImportError, match="aoslib.world"):
        __import__("aoslib.world")


def test_replacement_backend_serves_the_substitute_module(monkeypatch, stub_parent_packages):
    substitute = types.ModuleType(native_modules.replacement_name("shared.glm"))
    substitute.MARKER = "substitute"
    monkeypatch.setitem(sys.modules, native_modules.replacement_name("shared.glm"), substitute)
    monkeypatch.delitem(sys.modules, "shared.glm", raising=False)

    native_modules.install({"shared.glm": native_modules.REPLACEMENT})
    __import__("shared.glm")

    assert sys.modules["shared.glm"] is substitute
    assert sys.modules["shared.glm"].MARKER == "substitute"
    # It must answer to the name the client imported, not its own file name.
    assert sys.modules["shared.glm"].__name__ == "shared.glm"


def test_replacement_name_flattens_nested_modules():
    assert (
        native_modules.replacement_name("aoslib.scenes.main.player")
        == "port.replacements.aoslib_scenes_main_player"
    )


def test_configuration_is_parsed_into_routes():
    routes = native_modules.parse_configuration("shared.glm=replacement, aoslib.world=stub")
    assert routes == {
        "shared.glm": native_modules.REPLACEMENT,
        "aoslib.world": native_modules.STUB,
    }


def test_empty_configuration_is_accepted():
    assert native_modules.parse_configuration("") == {}
    assert native_modules.parse_configuration(None) == {}


def test_unknown_module_is_rejected():
    with pytest.raises(native_modules.UnknownModule, match="aoslib.nonexistent"):
        native_modules.parse_configuration("aoslib.nonexistent=stub")


def test_unknown_backend_is_rejected():
    with pytest.raises(native_modules.UnknownBackend, match="sideways"):
        native_modules.parse_configuration("shared.glm=sideways")


def test_malformed_configuration_entry_is_rejected():
    with pytest.raises(native_modules.UnknownBackend, match="module=backend"):
        native_modules.parse_configuration("shared.glm")


def test_configuration_is_read_from_the_environment(monkeypatch):
    monkeypatch.setenv(native_modules.CONFIG_VARIABLE, "aoslib.world=stub")
    summary = native_modules.status()
    assert summary[native_modules.STUB] == ["aoslib.world"]


def test_registry_matches_the_extension_modules_in_the_tree():
    """The registry is the port checklist, so it must not drift from reality."""
    found = set()
    for pyd in list(PROJECT_ROOT.glob("aoslib/**/*.pyd")) + list(PROJECT_ROOT.glob("shared/*.pyd")):
        relative = pyd.relative_to(PROJECT_ROOT).with_suffix("")
        found.add(".".join(relative.parts))

    # steam.pyd was removed once shared/steam.py replaced it; enet is an
    # unmodified third-party binding rather than game code.
    assert found == set(native_modules.NATIVE_MODULES)
