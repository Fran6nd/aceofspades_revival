"""Shared test setup.

The repository root contains a handful of 32-bit Python 2.7 stdlib extension
modules left over from the original game directory: `_socket.pyd`,
`_hashlib.pyd`, `bz2.pyd`, `pyexpat.pyd`, `select.pyd`, `unicodedata.pyd` and
`_win32sysloader.pyd`.

On Windows `.pyd` is a recognised extension suffix, so as soon as the
repository root is on `sys.path` those files shadow the real standard library.
A 64-bit Python 3 then fails with:

    ImportError: DLL load failed while importing _socket:
    %1 is not a valid Win32 application.

Every test module inserts the repository root at the front of `sys.path` so it
can import the client, which is exactly the condition that triggers this. The
modules are imported here first, before any test module runs, so they are
already resolved from the standard library and cached in `sys.modules`. A later
import of the same name is then satisfied from the cache and never reaches the
shadowing file.

This has no effect off Windows, where `.pyd` is not an importable suffix.
"""

import importlib

# Kept in step with the *.pyd files tracked in the repository root. Anything
# added there that collides with a stdlib module name belongs in this list.
_SHADOWED_BY_REPO_ROOT = (
    "_hashlib",
    "_socket",
    "bz2",
    "pyexpat",
    "select",
    "socket",
    "unicodedata",
)

for _name in _SHADOWED_BY_REPO_ROOT:
    try:
        importlib.import_module(_name)
    except ImportError:
        # Not every name is present on every platform; the point is only to win
        # the race against the shadowing file where it matters.
        pass
