"""Tests for the native module API reference generator.

The generated stubs are meant to be read and diffed by people, so the things
worth guarding are that they parse, that they are deterministic, and that they
never quietly invent information the introspection run did not provide.
"""

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

MODULE_PATH = PROJECT_ROOT / "tools" / "oracle" / "generate_api_reference.py"
SPEC = importlib.util.spec_from_file_location("generate_api_reference", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


def report_with(*modules):
    return {
        "python_version": "2.7.18 (default, x86)",
        "pointer_bits": 32,
        "modules": list(modules),
    }


def callable_entry(args=(), defaults=(), doc=None, varargs=None, keywords=None):
    return {
        "kind": "cython_function_or_method",
        "doc": doc,
        "signature": {
            "args": list(args),
            "defaults": list(defaults),
            "varargs": varargs,
            "keywords": keywords,
        },
    }


def write_report(tmp_path, report):
    path = tmp_path / "native_api.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    return path


def test_generated_stubs_are_valid_python(tmp_path):
    report = report_with(
        {
            "module": "shared.glm",
            "import": "package",
            "api": {
                "doc": "Vector maths.",
                "members": {
                    "PI": {"kind": "float", "value": "3.14159"},
                    "dot": callable_entry(["a", "b"], doc="Dot product."),
                    "opaque": {"kind": "builtin_function_or_method", "doc": None},
                    "Vector3": {
                        "kind": "class",
                        "doc": "A 3D vector.",
                        "bases": ["object"],
                        "members": {
                            "__init__": callable_entry(
                                ["self", "x", "y"], defaults=["0.0", "0.0"]
                            ),
                            "EPSILON": {"kind": "float", "value": "1e-06"},
                        },
                    },
                },
            },
        }
    )
    output = tmp_path / "api"
    generator.main.__globals__["sys"].argv = [
        "generate_api_reference.py",
        str(write_report(tmp_path, report)),
        str(output),
    ]
    assert generator.main() == 0

    stub = output / "shared.glm.pyi"
    ast.parse(stub.read_text(encoding="utf-8"))


def test_a_signature_that_could_not_be_read_is_marked_not_invented():
    entry = {"kind": "builtin_function_or_method", "doc": None}
    arguments, comment = generator.format_signature(entry)
    assert arguments == "(*args, **kwargs)"
    assert "not introspectable" in comment
    # The marker must be a comment, or the stub will not parse.
    rendered = "\n".join(generator.render_callable("opaque", entry, ""))
    ast.parse(rendered)


def test_defaults_bind_to_the_tail_of_the_argument_list():
    entry = callable_entry(["self", "x", "y", "z"], defaults=["1", "2"])
    arguments, _ = generator.format_signature(entry)
    assert arguments == "(self, x, y=1, z=2)"


def test_varargs_and_keywords_are_rendered():
    entry = callable_entry(["self"], varargs="args", keywords="kwargs")
    arguments, _ = generator.format_signature(entry)
    assert arguments == "(self, *args, **kwargs)"


def test_output_is_deterministic(tmp_path):
    members = {name: {"kind": "int", "value": "1"} for name in ("zeta", "alpha", "mu")}
    entry = {"module": "shared.glm", "import": "package", "api": {"members": members}}
    first = generator.render_module(entry)
    # Rebuild the dict in a different insertion order.
    reordered = {name: members[name] for name in ("mu", "zeta", "alpha")}
    second = generator.render_module(
        {"module": "shared.glm", "import": "package", "api": {"members": reordered}}
    )
    assert first == second


def test_crashed_modules_get_no_stub_but_are_listed(tmp_path):
    report = report_with(
        {"module": "aoslib.draw", "import": "crashed", "exit_code": -1073741819},
        {"module": "shared.lzf", "import": "package", "api": {"members": {}}},
    )
    output = tmp_path / "api"
    generator.main.__globals__["sys"].argv = [
        "generate_api_reference.py",
        str(write_report(tmp_path, report)),
        str(output),
    ]
    generator.main()

    assert not (output / "aoslib.draw.pyi").exists()
    index = (output / "README.md").read_text(encoding="utf-8")
    assert "aoslib.draw" in index
    assert "abort the interpreter" in index


def test_stale_stubs_are_removed(tmp_path):
    output = tmp_path / "api"
    output.mkdir()
    stale = output / "aoslib.gone.pyi"
    stale.write_text("# left over\n", encoding="utf-8")

    report = report_with({"module": "shared.lzf", "import": "package", "api": {"members": {}}})
    generator.main.__globals__["sys"].argv = [
        "generate_api_reference.py",
        str(write_report(tmp_path, report)),
        str(output),
    ]
    generator.main()

    assert not stale.exists(), "a module missing from the report must not leave a stale stub"


def test_missing_report_is_an_error(tmp_path):
    generator.main.__globals__["sys"].argv = [
        "generate_api_reference.py",
        str(tmp_path / "absent.json"),
        str(tmp_path / "api"),
    ]
    assert generator.main() == 1
