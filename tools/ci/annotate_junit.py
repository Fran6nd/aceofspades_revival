"""Turn a JUnit XML report into GitHub Actions annotations.

Workflow run logs require an authenticated request, but annotations are part of
the check run and are readable on a public repository without one. Emitting
failures this way means a red build can be diagnosed from the API alone,
instead of needing someone to open the web UI and copy the traceback out.

Usage:
    python tools/ci/annotate_junit.py results.xml
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path

# Annotations are truncated in the UI beyond roughly this length, and the
# useful part of a pytest failure is the assertion at the end rather than the
# frames leading up to it.
MAX_MESSAGE = 3500


def escape(value: str) -> str:
    """Escape the workflow-command delimiters, not general text."""
    return (
        value.replace('%', '%25')
        .replace('\r', '%0D')
        .replace('\n', '%0A')
        .replace(':', '%3A')
        .replace(',', '%2C')
    )


def tail(text: str, limit: int = MAX_MESSAGE) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return '...\n' + text[-limit:]


def annotate_raw_log(log_path: Path, reason: str) -> None:
    """Fall back to the captured output when there is no structured report.

    A process that dies during collection, or before it starts at all, produces
    no JUnit XML. That is exactly the case worth surfacing, because the run log
    itself needs an authenticated request to read.
    """
    if not log_path or not log_path.is_file():
        print(f'::error::{reason}, and no captured output at {log_path} either')
        return
    text = log_path.read_text(encoding='utf-8', errors='replace')
    if not text.strip():
        print(f'::error::{reason}, and the captured output was empty')
        return
    print(f'::error title=No structured report::{escape(reason)}%0A%0A{escape(tail(text))}')


def annotate(report_path: Path, fallback_log: Path | None = None) -> int:
    if not report_path.is_file():
        annotate_raw_log(fallback_log, f'No report at {report_path}')
        return 0

    tree = ElementTree.parse(report_path)
    failures = 0

    for testcase in tree.iter('testcase'):
        for outcome in list(testcase.findall('failure')) + list(testcase.findall('error')):
            failures += 1
            classname = testcase.get('classname', '')
            name = testcase.get('name', '<unknown>')
            # classname is the dotted module path; recover a file path so the
            # annotation attaches to the right place in the diff.
            file_hint = testcase.get('file') or (classname.split('.')[0].replace('.', '/') + '.py')
            line = testcase.get('line', '1')
            detail = (outcome.get('message') or '') + '\n' + (outcome.text or '')
            title = f'{classname}.{name}' if classname else name
            print(
                f'::error file={file_hint},line={line},title={escape(title)}::'
                f'{escape(tail(detail))}'
            )

    if failures:
        print(f'::notice::Annotated {failures} failing test(s)')
    return failures


def main() -> int:
    if len(sys.argv) < 2:
        print('usage: annotate_junit.py <junit-xml> [captured-output.txt]', file=sys.stderr)
        return 2
    fallback = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    annotate(Path(sys.argv[1]), fallback)
    # Never fail here: the workflow decides the outcome from the command it ran.
    # This step only reports.
    return 0


if __name__ == '__main__':
    sys.exit(main())
