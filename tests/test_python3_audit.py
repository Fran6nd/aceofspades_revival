"""Tests for the Python 3 compatibility audit.

The audit drives migration planning, so the risk worth guarding against is that
it quietly under-reports: a file that is missed looks like one less thing to
fix rather than a bug in the tool.
"""

import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

MODULE_PATH = PROJECT_ROOT / "tools" / "port" / "audit_python3.py"
SPEC = importlib.util.spec_from_file_location("audit_python3", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def classify_source(tmp_path, source, name="sample.py"):
    path = tmp_path / name
    path.write_text(source, encoding="utf-8")
    # classify() reports paths relative to the project root, so point it at the
    # temporary directory for the duration.
    original_root = audit.PROJECT_ROOT
    audit.PROJECT_ROOT = tmp_path
    try:
        return audit.classify(path)
    finally:
        audit.PROJECT_ROOT = original_root


def test_print_statement_is_reported_as_unparseable(tmp_path):
    entry = classify_source(tmp_path, "print 'hello'\n")
    assert entry["status"] == "unparseable"
    assert entry["cause"] == "print statement"


def test_long_literal_is_distinguished_from_a_print_statement(tmp_path):
    entry = classify_source(tmp_path, "value = 4273777538L\n")
    assert entry["status"] == "unparseable"
    assert entry["cause"] == "long literal (123L)"


def test_clean_python3_source_has_no_findings(tmp_path):
    entry = classify_source(tmp_path, "def add(a, b):\n    return a + b\n")
    assert entry["status"] == "parses"
    assert entry["idioms"] == {}


def test_runtime_idioms_are_detected_in_parseable_source(tmp_path):
    entry = classify_source(
        tmp_path,
        "def walk(mapping):\n"
        "    for index in xrange(10):\n"
        "        pass\n"
        "    return mapping.iteritems()\n",
    )
    assert entry["status"] == "parses"
    assert entry["idioms"]["xrange"] == 1
    assert entry["idioms"]["iteritems/iterkeys/itervalues"] == 1


def test_commented_out_idioms_are_not_counted(tmp_path):
    entry = classify_source(tmp_path, "# for i in xrange(10):\nvalue = 1\n")
    assert entry["idioms"] == {}


def test_print_as_a_function_is_not_flagged(tmp_path):
    """`print(...)` is valid in both languages and must not be a false positive."""
    entry = classify_source(tmp_path, "print('hello')\n")
    assert entry["status"] == "parses"


def test_the_audit_runs_over_the_real_tree():
    """A smoke test: the tool must survive the actual repository."""
    results = [audit.classify(path) for path in audit.source_files()]
    assert results, "the audit found no source files at all"
    assert all("status" in entry for entry in results)
    # Every parse failure must be attributed, or the migration plan is guessing.
    for entry in results:
        if entry["status"] == "unparseable":
            assert entry["cause"] != "unclassified", entry["path"]
