"""Audit the tree for Python 3 compatibility.

Two questions, answered separately because they cost very different amounts to
fix:

1. Does the file parse under Python 3 at all? A file that does not parse is a
   hard blocker - nothing can import it, and tests have to resort to slicing
   source out textually.
2. If it parses, which Python 2 idioms does it still contain? These are the
   quiet ones: `d.iteritems()` parses perfectly well under Python 3 and then
   fails at runtime.

Usage:
    python tools/port/audit_python3.py            # summary
    python tools/port/audit_python3.py --json     # machine readable
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Not client code: generated output, third-party bytecode, the test suite
# (already Python 3), and the tooling written for this port.
EXCLUDED_DIRECTORIES = {
    '.git',
    'build',
    'vendor',
    'tests',
    'tools',
    'port',
    '_markerlib',
    'aceofspades_decompiled',
    'python',
}

# Idioms that parse under Python 3 but do not behave the same, or fail at
# runtime. Each is (label, compiled pattern). Deliberately conservative: a
# missed idiom is better than a false positive that wastes review time.
RUNTIME_IDIOMS = [
    ('iteritems/iterkeys/itervalues', re.compile(r'\.iter(items|keys|values)\s*\(')),
    ('has_key', re.compile(r'\.has_key\s*\(')),
    ('unicode()', re.compile(r'(?<![\w.])unicode\s*\(')),
    ('basestring', re.compile(r'(?<![\w.])basestring(?![\w])')),
    ('xrange', re.compile(r'(?<![\w.])xrange\s*\(')),
    ('long()', re.compile(r'(?<![\w.])long\s*\(')),
    ('raw_input', re.compile(r'(?<![\w.])raw_input\s*\(')),
    ('cmp()', re.compile(r'(?<![\w.])cmp\s*\(')),
    ('StringIO/cStringIO', re.compile(r'(?<![\w.])(cStringIO|StringIO)(?![\w])')),
    ('urllib2/urlparse', re.compile(r'(?<![\w.])(urllib2|urlparse)(?![\w])')),
    ('Tkinter (py2 casing)', re.compile(r'(?<![\w.])(Tkinter|tkMessageBox|tkSimpleDialog|ttk)(?![\w])')),
    ('ConfigParser (py2 casing)', re.compile(r'(?<![\w.])ConfigParser(?![\w])')),
    ('Queue (py2 casing)', re.compile(r'(?<![\w.])Queue(?![\w])')),
    ('cPickle', re.compile(r'(?<![\w.])cPickle(?![\w])')),
    ('sort(cmp=)', re.compile(r'\.sort\s*\(\s*cmp\s*=')),
    ('dict.keys() indexed', re.compile(r'\.keys\s*\(\s*\)\s*\[')),
]


# Syntax that Python 3 removed outright. Grouping parse failures by cause
# matters because the fixes are not comparable: long literals are a mechanical
# suffix strip, whereas `except X, e` and backticks need real edits.
PARSE_FAILURE_CAUSES = [
    # Checked before `print`, because a file can contain both and this one has
    # no Python 3 equivalent - it needs a real edit, not a mechanical rewrite.
    ('tuple parameter unpacking', re.compile(r'^\s*def\s+\w+\s*\((\s*self\s*,)?\s*\(', re.M)),
    ('print statement', re.compile(r'^\s*print\s+[^(=]', re.M)),
    ('long literal (123L)', re.compile(r'(?<![\w.])\d+[lL](?![\w])')),
    ('except X, e', re.compile(r'^\s*except\s+[^\n:]+,\s*\w+\s*:', re.M)),
    ('octal literal (0777)', re.compile(r'(?<![\w.])0[0-7]{2,}(?![\w.])')),
    ('backtick repr', re.compile(r'`[^`\n]+`')),
    ('raise X, Y', re.compile(r'^\s*raise\s+\w+\s*,', re.M)),
    ('exec statement', re.compile(r'^\s*exec\s+[^(=]', re.M)),
    ('<> operator', re.compile(r'<>')),
]


def parse_failure_cause(text: str, error: SyntaxError) -> str:
    """Name the Python 2 construct responsible, for planning the fix."""
    # Prefer the construct on the reported line; fall back to a whole-file scan
    # because the first failure masks everything after it.
    lines = text.splitlines()
    if error.lineno and 0 < error.lineno <= len(lines):
        offending = lines[error.lineno - 1]
        for label, pattern in PARSE_FAILURE_CAUSES:
            if pattern.search(offending):
                return label
    for label, pattern in PARSE_FAILURE_CAUSES:
        if pattern.search(text):
            return label
    return 'unclassified'


def source_files():
    for path in sorted(PROJECT_ROOT.rglob('*.py')):
        relative = path.relative_to(PROJECT_ROOT)
        if any(part in EXCLUDED_DIRECTORIES for part in relative.parts):
            continue
        yield path


def classify(path: Path) -> dict:
    relative = str(path.relative_to(PROJECT_ROOT))
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except OSError as error:
        return {'path': relative, 'status': 'unreadable', 'detail': str(error)}

    entry: dict = {'path': relative, 'lines': len(text.splitlines())}
    try:
        ast.parse(text)
    except SyntaxError as error:
        entry['status'] = 'unparseable'
        entry['detail'] = f'{error.msg} (line {error.lineno})'
        entry['cause'] = parse_failure_cause(text, error)
        return entry

    entry['status'] = 'parses'
    idioms: dict[str, int] = {}
    for label, pattern in RUNTIME_IDIOMS:
        # Strip comment-only matches cheaply; a full-fidelity pass is not worth
        # it for a triage tool.
        hits = sum(
            1
            for line in text.splitlines()
            if pattern.search(line) and not line.lstrip().startswith('#')
        )
        if hits:
            idioms[label] = hits
    entry['idioms'] = idioms
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='emit the full result as JSON')
    arguments = parser.parse_args()

    results = [classify(path) for path in source_files()]

    if arguments.json:
        json.dump(results, sys.stdout, indent=2, sort_keys=True)
        return 0

    unparseable = [r for r in results if r['status'] == 'unparseable']
    with_idioms = [r for r in results if r.get('idioms')]
    clean = [r for r in results if r['status'] == 'parses' and not r.get('idioms')]

    print('Python 3 compatibility audit')
    print('=' * 60)
    print(f'files scanned      : {len(results)}')
    print(f'clean              : {len(clean)}')
    print(f'runtime idioms only: {len(with_idioms)}')
    print(f'do not parse       : {len(unparseable)}')
    print()

    if unparseable:
        by_cause: dict[str, list[str]] = {}
        for entry in unparseable:
            by_cause.setdefault(entry.get('cause', 'unclassified'), []).append(entry['path'])

        print('Files Python 3 cannot parse (hard blockers)')
        print('-' * 60)
        for cause, paths in sorted(by_cause.items(), key=lambda item: -len(item[1])):
            print(f'  {len(paths):3d}  {cause}')
            for path in paths:
                print(f'         {path}')
        print()

    totals: dict[str, int] = {}
    for entry in with_idioms:
        for label, count in entry['idioms'].items():
            totals[label] = totals.get(label, 0) + count

    if totals:
        print('Python 2 idioms that parse but misbehave')
        print('-' * 60)
        for label, count in sorted(totals.items(), key=lambda item: -item[1]):
            files = sum(1 for e in with_idioms if label in e['idioms'])
            print(f'  {count:5d} occurrences in {files:3d} files  {label}')
        print()

    print('Worst files by idiom count')
    print('-' * 60)
    ranked = sorted(with_idioms, key=lambda e: -sum(e['idioms'].values()))
    for entry in ranked[:15]:
        total = sum(entry['idioms'].values())
        print(f"  {total:4d}  {entry['path']}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
