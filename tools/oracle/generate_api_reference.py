"""Turn an introspection report into a readable, diffable API reference.

The report itself is a large JSON blob produced on a Windows runner. This
renders it as one stub file per module plus an index, so the API of the native
modules can be read, reviewed and diffed on any machine - which is the whole
point of capturing it.

Output is deterministic: everything is sorted, so a change in the reference
means the modules actually changed, not that the walk order did.

Usage:
    python tools/oracle/generate_api_reference.py native_api.json port/api
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HEADER = """# Generated from a native module introspection run. Do not edit by hand.
#
# Source: {module} ({backend})
# Regenerate with tools/oracle/generate_api_reference.py
"""

# Members every module or class carries regardless of what it does; listing them
# would bury the parts that matter.
UNINTERESTING = {
    '__builtins__',
    '__doc__',
    '__file__',
    '__loader__',
    '__name__',
    '__package__',
    '__path__',
    '__spec__',
    '__test__',
}


def format_signature(entry: dict) -> tuple[str, str]:
    """Return the argument list and any trailing comment.

    The comment is kept separate so it can be placed after the colon; inlining
    it into the argument list produces a stub that will not parse.
    """
    signature = entry.get('signature')
    if not signature:
        # A plain C function exposes no argument metadata at all. Say so rather
        # than inventing a signature that looks authoritative.
        return '(*args, **kwargs)', '  # signature not introspectable'

    parts: list[str] = []
    args = signature.get('args') or []
    defaults = signature.get('defaults') or []
    # Defaults bind to the tail of the argument list.
    first_default = len(args) - len(defaults)
    for index, name in enumerate(args):
        if index >= first_default:
            parts.append(f'{name}={defaults[index - first_default]}')
        else:
            parts.append(name)
    if signature.get('varargs'):
        parts.append('*' + signature['varargs'])
    if signature.get('keywords'):
        parts.append('**' + signature['keywords'])
    return '(' + ', '.join(parts) + ')', ''


def render_docstring(doc: str | None, indent: str) -> list[str]:
    if not doc:
        return []
    text = doc.strip()
    if not text:
        return []
    lines = text.splitlines()
    if len(lines) == 1:
        return [f'{indent}"""{lines[0]}"""']
    rendered = [f'{indent}"""{lines[0]}']
    rendered.extend(f'{indent}{line}' for line in lines[1:])
    rendered.append(f'{indent}"""')
    return rendered


def render_callable(name: str, entry: dict, indent: str) -> list[str]:
    arguments, comment = format_signature(entry)
    lines = [f'{indent}def {name}{arguments}:{comment}']
    doc = render_docstring(entry.get('doc'), indent + '    ')
    lines.extend(doc)
    lines.append(f'{indent}    ...')
    return lines


def render_class(name: str, entry: dict) -> list[str]:
    bases = entry.get('bases') or []
    inherits = f"({', '.join(bases)})" if bases else ''
    lines = [f'class {name}{inherits}:']
    lines.extend(render_docstring(entry.get('doc'), '    '))

    members = entry.get('members') or {}
    body: list[str] = []
    for member_name in sorted(members):
        if member_name in UNINTERESTING:
            continue
        member = members[member_name]
        kind = member.get('kind', '')
        if kind in ('class',):
            continue
        if 'signature' in member or kind.endswith('method') or kind in ('function', 'cython_function_or_method', 'builtin_function_or_method'):
            body.extend(render_callable(member_name, member, '    '))
        else:
            body.append(f"    {member_name}: {kind}  # {member.get('value', '')}")

    if not body:
        body = ['    ...']
    lines.extend(body)
    return lines


def render_module(entry: dict) -> str:
    name = entry.get('module', '?')
    backend = entry.get('import', '?')
    lines = [HEADER.format(module=name, backend=backend)]

    api = entry.get('api') or {}
    lines.extend(render_docstring(api.get('doc'), ''))

    members = api.get('members') or {}
    constants: list[str] = []
    functions: list[str] = []
    classes: list[str] = []

    for member_name in sorted(members):
        if member_name in UNINTERESTING:
            continue
        member = members[member_name]
        kind = member.get('kind', '')
        if kind == 'class':
            classes.append('\n'.join(render_class(member_name, member)))
        elif 'signature' in member or kind in (
            'function',
            'builtin_function_or_method',
            'cython_function_or_method',
        ):
            functions.append('\n'.join(render_callable(member_name, member, '')))
        else:
            constants.append(f"{member_name}: {kind}  # {member.get('value', '')}")

    if constants:
        lines.append('# Constants\n' + '\n'.join(constants))
    if functions:
        lines.append('# Functions\n' + '\n\n'.join(functions))
    if classes:
        lines.append('# Classes\n' + '\n\n\n'.join(classes))

    if not (constants or functions or classes):
        lines.append('# No introspectable members were reachable.')

    return '\n\n'.join(part for part in lines if part.strip()) + '\n'


def render_index(report: dict) -> str:
    modules = report.get('modules', [])
    lines = [
        '# Native Module API Reference',
        '',
        'Captured by importing the shipped extension modules under 32-bit',
        'Python 2.7 on Windows, which is the only place they load. Generated;',
        'do not edit by hand.',
        '',
        f"- interpreter: `{report.get('python_version', '?').splitlines()[0]}`",
        f"- pointer width: {report.get('pointer_bits', '?')}-bit",
        '',
        'Most modules star-import a large shared constants namespace, so the',
        'raw member count is dominated by names the module merely re-exports.',
        '"own" counts those not also present in `shared.common`, and is the',
        'number that reflects what a module actually implements.',
        '',
        '| module | status | members | own |',
        '| --- | --- | --- | --- |',
    ]

    # The namespace every module re-exports, used to separate what a module
    # implements from what it inherits by star import.
    shared_namespace: set[str] = set()
    for entry in modules:
        if entry.get('module') == 'shared.common':
            shared_namespace = set((entry.get('api') or {}).get('members') or {})
            break

    for entry in sorted(modules, key=lambda item: item.get('module', '')):
        name = entry.get('module', '?')
        status = entry.get('import', '?')
        members = set((entry.get('api') or {}).get('members') or {})
        own = members - shared_namespace if name != 'shared.common' else members
        link = f'[`{name}`]({name}.pyi)' if status not in ('failed', 'crashed') else f'`{name}`'
        lines.append(f'| {link} | {status} | {len(members)} | {len(own)} |')

    crashed = [m['module'] for m in modules if m.get('import') == 'crashed']
    if crashed:
        lines.extend([
            '',
            '## Modules that abort the interpreter',
            '',
            'These terminate the process rather than raising, so they cannot be',
            'introspected on a runner with no GPU or display. Their API has to be',
            'recovered statically instead.',
            '',
        ])
        lines.extend(f'- `{name}`' for name in sorted(crashed))

    return '\n'.join(lines) + '\n'


def main() -> int:
    if len(sys.argv) < 3:
        print('usage: generate_api_reference.py <native_api.json> <output-dir>', file=sys.stderr)
        return 2

    report_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    if not report_path.is_file():
        print(f'No introspection report at {report_path}', file=sys.stderr)
        return 1

    report = json.loads(report_path.read_text(encoding='utf-8', errors='replace'))
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clear previously generated stubs so a module that disappears from the
    # report does not leave a stale file behind claiming it still exists.
    for stale in output_dir.glob('*.pyi'):
        stale.unlink()

    written = 0
    for entry in report.get('modules', []):
        if entry.get('import') in ('failed', 'crashed'):
            continue
        name = entry.get('module')
        if not name:
            continue
        (output_dir / f'{name}.pyi').write_text(render_module(entry), encoding='utf-8')
        written += 1

    (output_dir / 'README.md').write_text(render_index(report), encoding='utf-8')
    print(f'wrote {written} stub files and an index to {output_dir}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
