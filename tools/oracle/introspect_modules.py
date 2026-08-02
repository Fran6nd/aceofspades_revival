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


def main():
    prepare_environment()

    destination = sys.argv[1] if len(sys.argv) > 1 else 'native_api.json'
    report = {
        'python_version': sys.version,
        'platform': sys.platform,
        'pointer_bits': 8 * struct.calcsize('P'),
        'modules': [],
    }

    for name in MODULES:
        print('probing %s' % name)
        # Record the attempt before making it. A module that initialises a GL
        # context can abort the process outright rather than raise, which no
        # amount of exception handling would catch, so the report is flushed
        # after every step and carries the name of whatever was in flight.
        report['in_flight'] = name
        write_report(report, destination)

        entry = probe(name)
        report['modules'].append(entry)
        report.pop('in_flight', None)
        write_report(report, destination)
        print('  -> %s' % entry['import'])

    write_report(report, destination)

    succeeded = [m for m in report['modules'] if m['import'] != 'failed']
    print('')
    print('imported %d of %d modules' % (len(succeeded), len(MODULES)))
    print('wrote %s' % destination)

    # Always exit 0: a module that cannot be imported headlessly is a result to
    # record, not a build failure. The report is the deliverable.
    return 0


if __name__ == '__main__':
    sys.exit(main())
