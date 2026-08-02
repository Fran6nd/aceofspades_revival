# -*- coding: utf-8 -*-
"""Dump the public API of the game's native extension modules.

The shipped `.pyd` modules are 32-bit Windows extensions built for Python 2.7,
so they can only be loaded by that interpreter on real Windows. This script
runs there, imports each module, and records everything reachable by
introspection: classes, bases, methods, functions, constants, signatures and
docstrings.

The modules were produced by Cython with `binding=True`, which gives compiled
functions real `__code__` and `__defaults__` attributes, so `getargspec` can
recover argument names that a plain C extension would not expose.

The result is a JSON file. Once captured it is platform independent, which is
the point: the reimplementation work happens on macOS and Linux against this
file rather than against a Windows machine.

Written to run under Python 2.7, but kept 2/3 compatible so its logic can be
exercised off-Windows.
"""

from __future__ import print_function

import json
import os
import struct
import sys
import traceback


# Ordered so that leaves come first. A module that fails to import can leave a
# partially initialised entry in sys.modules, which then poisons anything that
# imports it, so the ones with no dependencies are attempted first to keep the
# failure reports honest.
MODULES = [
    # Leaves: no references to other project modules.
    'shared.lzf',
    'shared.glm',
    'shared.bytes',
    'shared.packet',
    'aoslib.font',
    'aoslib.customimage',
    'aoslib.physfs',
    # Depend only on the leaves above.
    'shared.common',
    'shared.shrapnelManager',
    'aoslib.kv6',
    'aoslib.gl',
    'aoslib.mesh',
    # Mid tier.
    'aoslib.world',
    'aoslib.vxl',
    'shared.explosionDamageManager',
    'aoslib.draw',
    'aoslib.network',
    'aoslib.character',
    # Heaviest, and the most likely to need a display or GL context.
    'aoslib.ugc_data',
    'aoslib.gamemanager',
    'aoslib.scenes.main.player',
    'aoslib.hud.hud',
    'aoslib.scenes.main.gameScene',
]

# Skipped deliberately: pywin32 and the stdlib extension modules shipped in the
# repo root are not game code, and enet is an unmodified third-party binding.
MAX_REPR = 200


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def prepare_environment():
    """Make the repo importable and its bundled DLLs discoverable.

    Several modules link against glew32, physfs and the OpenAL runtime, which
    live in the repo root rather than on the system path.
    """
    root = repo_root()
    os.chdir(root)
    if root not in sys.path:
        sys.path.insert(0, root)

    vendor = os.path.join(root, 'vendor')
    if os.path.isdir(vendor) and vendor not in sys.path:
        sys.path.insert(1, vendor)

    os.environ['PATH'] = root + os.pathsep + os.environ.get('PATH', '')
    # Python 3.8+ on Windows stopped honouring PATH for extension module
    # dependencies. Harmless to call defensively when the attribute exists.
    if hasattr(os, 'add_dll_directory') and os.name == 'nt':
        try:
            os.add_dll_directory(root)
        except OSError:
            pass


def safe_repr(value):
    try:
        text = repr(value)
    except Exception as error:
        return '<unrepresentable: %s>' % type(error).__name__
    if len(text) > MAX_REPR:
        text = text[:MAX_REPR] + '...'
    return text


def describe_signature(obj):
    """Recover an argument list, preferring the richest source available."""
    try:
        import inspect
    except ImportError:
        return None

    getargspec = getattr(inspect, 'getfullargspec', None) or getattr(inspect, 'getargspec', None)
    if getargspec is None:
        return None
    try:
        spec = getargspec(obj)
    except Exception:
        # Plain C functions and slot wrappers expose no argument metadata.
        return None
    return {
        'args': list(spec.args or []),
        'varargs': spec.varargs,
        'keywords': getattr(spec, 'varkw', None) or getattr(spec, 'keywords', None),
        'defaults': [safe_repr(default) for default in (spec.defaults or ())],
    }


def describe_callable(obj):
    entry = {
        'kind': type(obj).__name__,
        'doc': getattr(obj, '__doc__', None),
    }
    signature = describe_signature(obj)
    if signature is not None:
        entry['signature'] = signature
    return entry


def describe_class(cls):
    entry = {
        'kind': 'class',
        'doc': getattr(cls, '__doc__', None),
        'bases': [getattr(base, '__name__', safe_repr(base)) for base in getattr(cls, '__bases__', ())],
        'members': {},
    }
    for name in sorted(dir(cls)):
        if name.startswith('__') and name.endswith('__') and name not in ('__init__', '__call__'):
            continue
        try:
            member = getattr(cls, name)
        except Exception as error:
            entry['members'][name] = {'kind': '<unreadable: %s>' % type(error).__name__}
            continue
        if callable(member):
            entry['members'][name] = describe_callable(member)
        else:
            entry['members'][name] = {
                'kind': type(member).__name__,
                'value': safe_repr(member),
            }
    return entry


def describe_module(module):
    entry = {'members': {}}
    doc = getattr(module, '__doc__', None)
    if doc:
        entry['doc'] = doc

    # Cython emits a __test__ dict of doctest fragments, which leaks snippets of
    # the original source. Worth keeping verbatim.
    test_table = getattr(module, '__test__', None)
    if isinstance(test_table, dict) and test_table:
        entry['cython_test_table'] = dict(
            (str(key), safe_repr(value)) for key, value in test_table.items()
        )

    for name in sorted(dir(module)):
        if name.startswith('__') and name.endswith('__'):
            continue
        try:
            member = getattr(module, name)
        except Exception as error:
            entry['members'][name] = {'kind': '<unreadable: %s>' % type(error).__name__}
            continue

        if isinstance(member, type) or type(member).__name__ in ('classobj', 'type'):
            entry['members'][name] = describe_class(member)
        elif callable(member):
            entry['members'][name] = describe_callable(member)
        else:
            entry['members'][name] = {
                'kind': type(member).__name__,
                'value': safe_repr(member),
            }
    return entry


def import_via_package(name):
    __import__(name)
    return sys.modules[name]


def import_isolated(name):
    """Load the extension file directly, bypassing its package __init__.

    `import aoslib.world` also executes `aoslib/__init__.py`, which imports the
    native font module and the graphics manager. When that chain is what fails,
    loading the file on its own separates "this module is broken" from "its
    package is".
    """
    import imp

    relative = name.split('.')
    path = os.path.join(repo_root(), *relative) + '.pyd'
    if not os.path.isfile(path):
        raise ImportError('no extension file at %s' % path)
    # The module init symbol is keyed on the final component only.
    return imp.load_dynamic(relative[-1], path)


def probe(name):
    result = {'module': name}
    try:
        module = import_via_package(name)
        result['import'] = 'package'
    except Exception:
        result['package_import_error'] = traceback.format_exc()
        try:
            module = import_isolated(name)
            result['import'] = 'isolated'
        except Exception:
            result['import'] = 'failed'
            result['isolated_import_error'] = traceback.format_exc()
            return result

    try:
        result['api'] = describe_module(module)
    except Exception:
        result['introspection_error'] = traceback.format_exc()
    return result


def write_report(report, destination):
    directory = os.path.dirname(os.path.abspath(destination))
    if directory and not os.path.isdir(directory):
        os.makedirs(directory)
    with open(destination, 'w') as handle:
        json.dump(report, handle, indent=2, sort_keys=True)


def probe_in_subprocess(name):
    """Probe one module in a child process.

    Some modules abort the interpreter instead of raising - `aoslib.draw` does
    this on a runner with no GPU. That cannot be caught, so it has to be
    contained: each module gets its own process, and a crash costs that module
    rather than every module after it.
    """
    import subprocess
    import tempfile

    handle, temporary = tempfile.mkstemp(suffix='.json')
    os.close(handle)
    try:
        command = [sys.executable, os.path.abspath(__file__), '--module', name, temporary]
        child = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=repo_root(),
        )
        output = child.communicate()[0]
        if not isinstance(output, str):
            output = output.decode('utf-8', 'replace')

        if child.returncode == 0:
            try:
                with open(temporary) as report_handle:
                    return json.load(report_handle)
            except (ValueError, IOError):
                pass

        return {
            'module': name,
            'import': 'crashed',
            'exit_code': child.returncode,
            'output': output[-4000:],
        }
    finally:
        if os.path.isfile(temporary):
            os.unlink(temporary)


def main():
    prepare_environment()

    # Child mode: probe exactly one module and write it out. Kept in the same
    # file so there is one harness to maintain, not two.
    if len(sys.argv) > 2 and sys.argv[1] == '--module':
        name = sys.argv[2]
        destination = sys.argv[3] if len(sys.argv) > 3 else 'module.json'
        write_report(probe(name), destination)
        return 0

    destination = sys.argv[1] if len(sys.argv) > 1 else 'native_api.json'
    report = {
        'python_version': sys.version,
        'platform': sys.platform,
        'pointer_bits': 8 * struct.calcsize('P'),
        'modules': [],
    }

    for name in MODULES:
        print('probing %s' % name)
        entry = probe_in_subprocess(name)
        report['modules'].append(entry)
        write_report(report, destination)
        print('  -> %s' % entry.get('import'))

    write_report(report, destination)

    imported = [m for m in report['modules'] if m.get('import') not in ('failed', 'crashed')]
    crashed = [m for m in report['modules'] if m.get('import') == 'crashed']
    print('')
    print('imported %d of %d modules' % (len(imported), len(MODULES)))
    if crashed:
        print('crashed: %s' % ', '.join(m['module'] for m in crashed))
    print('wrote %s' % destination)

    # Always exit 0. A module that cannot be loaded headlessly is a result to
    # record, not a build failure - finding that out is the point of this job.
    return 0


if __name__ == '__main__':
    sys.exit(main())
