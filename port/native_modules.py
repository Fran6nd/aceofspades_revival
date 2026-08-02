# -*- coding: utf-8 -*-
"""Route each native module to the original extension or to a replacement.

The client imports 24 native extension modules that only exist as 32-bit
Windows binaries. Replacing them all at once is not workable, so this installs
an import hook that decides, per module, where `import aoslib.world` should
actually come from:

    original     load the shipped .pyd through the normal import machinery
    replacement  load port.replacements.<name> and serve it under the real name
    stub         refuse the import with a message naming the module

`original` is the default for every module, so installing the hook with no
configuration leaves the client behaving exactly as it does today. That
property matters: the hook has to be invisible until it is asked to do
something.

Configuration comes from the AOS_PORT_MODULES environment variable, as a comma
separated list of `module=backend` pairs:

    AOS_PORT_MODULES="shared.glm=replacement,aoslib.world=stub"

Python compatibility: 2.7 and 3.x.
"""

from __future__ import absolute_import

import os
import sys

ORIGINAL = 'original'
REPLACEMENT = 'replacement'
STUB = 'stub'

BACKENDS = (ORIGINAL, REPLACEMENT, STUB)

CONFIG_VARIABLE = 'AOS_PORT_MODULES'

# Every native extension module the client imports. Keeping the full list here
# rather than discovering it means an unlisted module is an error rather than a
# silent pass-through, and it doubles as the checklist for the port.
NATIVE_MODULES = (
    'aoslib.character',
    'aoslib.customimage',
    'aoslib.draw',
    'aoslib.font',
    'aoslib.gamemanager',
    'aoslib.gl',
    'aoslib.hud.hud',
    'aoslib.kv6',
    'aoslib.mesh',
    'aoslib.network',
    'aoslib.physfs',
    'aoslib.scenes.main.gameScene',
    'aoslib.scenes.main.player',
    'aoslib.ugc_data',
    'aoslib.vxl',
    'aoslib.world',
    'shared.bytes',
    'shared.common',
    'shared.explosionDamageManager',
    'shared.glm',
    'shared.lzf',
    'shared.packet',
    'shared.shrapnelManager',
)

REPLACEMENT_PACKAGE = 'port.replacements'


class UnknownModule(ValueError):
    """Raised when the configuration names something that is not a native module."""


class UnknownBackend(ValueError):
    """Raised when the configuration names a backend that does not exist."""


def replacement_name(module_name):
    """Map a native module name onto its replacement module.

    Dots are flattened rather than nested so that `aoslib.scenes.main.player`
    does not require a package tree that mirrors the client's layout.
    """
    return '%s.%s' % (REPLACEMENT_PACKAGE, module_name.replace('.', '_'))


def parse_configuration(text):
    """Turn an AOS_PORT_MODULES value into a {module: backend} mapping."""
    routes = {}
    if not text:
        return routes
    for chunk in text.split(','):
        chunk = chunk.strip()
        if not chunk:
            continue
        if '=' not in chunk:
            raise UnknownBackend(
                'Malformed entry %r; expected module=backend' % chunk
            )
        name, backend = chunk.split('=', 1)
        name = name.strip()
        backend = backend.strip().lower()
        if name not in NATIVE_MODULES:
            raise UnknownModule(
                '%r is not a native module. Known modules: %s'
                % (name, ', '.join(NATIVE_MODULES))
            )
        if backend not in BACKENDS:
            raise UnknownBackend(
                '%r is not a backend for %s. Choose one of: %s'
                % (backend, name, ', '.join(BACKENDS))
            )
        routes[name] = backend
    return routes


class _Loader(object):
    """Serves a replacement module, or refuses the import for a stub."""

    def __init__(self, module_name, backend):
        self.module_name = module_name
        self.backend = backend

    def _resolve(self):
        if self.backend == STUB:
            raise ImportError(
                '%s is routed to a stub: it has not been ported yet. '
                'Set %s to route it elsewhere.' % (self.module_name, CONFIG_VARIABLE)
            )
        target = replacement_name(self.module_name)
        __import__(target)
        module = sys.modules[target]
        # Present the replacement under the name that was imported, so callers
        # and tracebacks refer to the module the client actually asked for.
        module.__name__ = self.module_name
        sys.modules[self.module_name] = module
        return module

    # Python 2 import protocol.
    def load_module(self, fullname):
        return self._resolve()

    # Python 3 import protocol. Returning a module from create_module makes it
    # the module object, so exec_module has nothing left to do.
    def create_module(self, spec):
        return self._resolve()

    def exec_module(self, module):
        return None


class NativeModuleFinder(object):
    """A sys.meta_path finder that applies the configured routes."""

    def __init__(self, routes=None):
        self.routes = dict(routes or {})

    def route_for(self, fullname):
        return self.routes.get(fullname, ORIGINAL)

    def _loader_for(self, fullname):
        backend = self.route_for(fullname)
        if backend == ORIGINAL:
            # Defer to the normal import machinery. This is what keeps the hook
            # invisible when nothing has been re-routed.
            return None
        return _Loader(fullname, backend)

    # Python 2 import protocol.
    def find_module(self, fullname, path=None):
        return self._loader_for(fullname)

    # Python 3 import protocol.
    def find_spec(self, fullname, path=None, target=None):
        loader = self._loader_for(fullname)
        if loader is None:
            return None
        from importlib.util import spec_from_loader

        return spec_from_loader(fullname, loader)


def install(routes=None):
    """Install the finder, replacing any previously installed one.

    Returns the finder so a caller can inspect or adjust the routes.
    """
    if routes is None:
        routes = parse_configuration(os.environ.get(CONFIG_VARIABLE))
    uninstall()
    finder = NativeModuleFinder(routes)
    # Ahead of the standard finders, otherwise the shipped .pyd wins.
    sys.meta_path.insert(0, finder)
    return finder


def uninstall():
    """Remove any installed finder. Safe to call when none is installed."""
    sys.meta_path[:] = [
        finder for finder in sys.meta_path if not isinstance(finder, NativeModuleFinder)
    ]


def status(routes=None):
    """Return {backend: [module, ...]}, for reporting port progress."""
    if routes is None:
        routes = parse_configuration(os.environ.get(CONFIG_VARIABLE))
    summary = dict((backend, []) for backend in BACKENDS)
    for name in NATIVE_MODULES:
        summary[routes.get(name, ORIGINAL)].append(name)
    return summary
