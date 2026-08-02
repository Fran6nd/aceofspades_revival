"""Summarise a native module introspection report.

Writes a table to the job summary and emits one annotation per module. Artifact
downloads need an authenticated request; annotations do not, so this is what
makes the result readable straight from the API.

Usage:
    python tools/ci/report_oracle.py build/oracle/native_api.json
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def escape(value: str) -> str:
    return (
        value.replace('%', '%25')
        .replace('\r', '%0D')
        .replace('\n', '%0A')
        .replace(':', '%3A')
        .replace(',', '%2C')
    )


def member_count(entry: dict) -> int:
    api = entry.get('api') or {}
    return len(api.get('members') or {})


def main() -> int:
    if len(sys.argv) < 2:
        print('usage: report_oracle.py <native_api.json>', file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f'::error::No introspection report at {path}')
        return 0

    report = json.loads(path.read_text(encoding='utf-8', errors='replace'))
    modules = report.get('modules', [])

    # Set while a module is being probed and cleared once it returns. If it is
    # still present, that module took the interpreter down with it rather than
    # raising, which is the failure mode a crash in native code produces.
    in_flight = report.get('in_flight')

    lines = [
        '## Native module introspection',
        '',
        f"- interpreter: `{report.get('python_version', '?').splitlines()[0]}`",
        f"- pointer width: {report.get('pointer_bits', '?')}-bit",
        f'- modules probed: {len(modules)}',
        '',
        '| module | import | members |',
        '| --- | --- | --- |',
    ]

    imported = 0
    for entry in modules:
        name = entry.get('module', '?')
        how = entry.get('import', '?')
        count = member_count(entry)
        if how not in ('failed', 'crashed'):
            imported += 1
        lines.append(f'| `{name}` | {how} | {count} |')

        if how == 'crashed':
            tail = '\n'.join((entry.get('output') or '').strip().splitlines()[-6:])
            print(
                f'::warning title={escape(name)} crashed the interpreter::'
                f'exit {entry.get("exit_code")}. It aborts rather than raising, so it '
                f'cannot be loaded here.%0A{escape(tail)}'
            )
        elif how == 'failed':
            detail = entry.get('isolated_import_error') or entry.get('package_import_error') or ''
            tail = '\n'.join(detail.strip().splitlines()[-6:])
            print(f'::warning title={escape(name)} could not be imported::{escape(tail)}')
        else:
            print(f'::notice title={escape(name)}::imported via {how}, {count} members')

    if in_flight:
        lines.append('')
        lines.append(f'**Interpreter died while probing `{in_flight}`.**')
        print(
            f'::error title=Crash while probing {escape(in_flight)}::'
            'The process terminated without raising, which points at a fault '
            'inside the native module rather than a Python-level error.'
        )

    lines.append('')
    lines.append(f'**{imported} of {len(modules)} modules imported.**')
    summary = '\n'.join(lines)

    print(summary)
    summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_path:
        with open(summary_path, 'a', encoding='utf-8') as handle:
            handle.write(summary + '\n')

    return 0


if __name__ == '__main__':
    sys.exit(main())
