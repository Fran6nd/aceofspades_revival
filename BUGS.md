# Known Bugs and Defects

Issues found while working on the cross-platform port. Kept here so that
findings made while investigating one thing are not lost when the work moves
on. Each entry cites where it lives and how it was confirmed.

Status: `FIXED` · `OPEN` · `WONTFIX`

---

## Build and release pipeline

### 1. Toolchain archives were downloaded without integrity verification — FIXED

`tools/build_legacy_release.py`

Five of the six bootstrapped toolchain archives (`altgraph`, `pywin32-ctypes`,
`pefile`, `dis3`, `future`) were fetched over HTTPS with no hash check. The
verification was written as "check the hash if one is present", and only
PyInstaller had one, so the absence of a hash silently disabled the check
rather than failing.

Fixed by pinning all five, each confirmed against both PyPI's published digest
and the actual downloaded bytes, and by making a missing hash a hard error so a
newly added component cannot repeat this. Covered by
`tests/test_build_release_security.py`.

### 2. Build output depended on whether UPX happened to be installed — FIXED

`tools/build_legacy_release.py`, spec template

`upx=True` is a request, not a requirement: PyInstaller silently skips
compression when UPX is not on PATH. The same commit therefore produced
different bytes and different checksums on different machines. It also worked
against the existing effort to avoid reputation-based antivirus false
positives, and was partly wasted regardless because `aos.exe` is overwritten
after packaging with the pinned bootloader.

Fixed by disabling UPX throughout, with the reasoning recorded above the spec
template.

### 3. Release build was impossible without the BattleSpades repository — FIXED

`tools/build_legacy_release.py`, `copy_server_bundle()`

The function raised unconditionally when the separate BattleSpades repo was not
checked out next to this one, and there was no flag or environment variable to
skip it. Any build in a clean environment was blocked.

Fixed by adding `--skip-server`, which stages a client-only release.

### 4. A 64-bit Python 2.7 produces a broken release with no error — FIXED

`tools/build_legacy_release.py`

Nothing anywhere asserts the interpreter's bitness. With a 64-bit Python 2.7,
PyInstaller's `matchDLLArch` silently drops every 32-bit `.pyd` and `.dll` in
the repo from the bundle. The build exits successfully and produces an
artifact that cannot run.

Fixed by `assert_build_interpreter_is_32bit()`, called from
`build_legacy_runtime()` so local builds are protected too, not just CI.

### 5. Asset staging has no existence guard — FIXED

`tools/build_legacy_release.py:810-816`, `copy_assets()`

`shutil.copytree(source, destination)` is called without checking that
`source` exists, so a missing asset directory raises `FileNotFoundError` from
inside the copy rather than a message naming the missing directory. All 14
directories are tracked, so this only surfaces under a sparse or partial
checkout — which is exactly the configuration someone would reach for to speed
up a 763 MB clone.

Fixed by checking each source directory and raising an error that names the
missing path and explains the likely cause.

### 6. Toolchain downloads have no timeout and no retry — FIXED

`tools/build_legacy_release.py`, `download_file()`

A bare `urllib.request.urlopen(url)` with no timeout argument and no retry
around six sequential PyPI fetches. A stalled connection hangs the build
indefinitely rather than failing. Only affects a cold toolchain cache.

Fixed with a 60 second timeout and three attempts. The download now writes to a
`.partial` file and renames on completion, so an interrupted transfer cannot be
mistaken for a finished one by the early return that skips existing files.

### 7. `tarfile.extractall` is called without an extraction filter — FIXED

`tools/build_legacy_release.py`, `extract_archive()`

Raises `DeprecationWarning` on Python 3.12 and 3.13, and changes behaviour on
3.14 where the default becomes `filter='data'`. Harmless for these plain-file
sdists today, but it will start warning and then behave differently as the
builder's own interpreter moves forward.

Fixed by requesting `filter='data'` where the interpreter supports it, which
also rejects archive members whose paths escape the destination directory.

### 8. Hidden `python27.dll` can be stranded by an abrupt kill — WONTFIX

`tools/build_legacy_release.py`

The build renames the repo's stale `python27.dll` to `python27.dll.buildhidden`
for the duration of the PyInstaller run. This *is* wrapped in `try/finally`, so
exceptions and non-zero exits restore it correctly. Only an abrupt process
termination (kill, power loss) would leave the working tree missing
`python27.dll`.

Recorded rather than fixed: the recovery is a one-line rename, and making it
crash-proof would mean a lock file or similar for very little gain.

---

## Client source

### 9. `shared.playerInteractions` is referenced but does not exist — OPEN

`shared/explosionDamageManager.pyd`

The compiled module references `shared.playerInteractions`. No such module
exists anywhere in the repository. Of the 43 distinct `aoslib.*` / `shared.*`
names referenced across all native modules, this is the only one absent.

Not yet known whether it is a live dependency on a code path that would crash,
or a dead reference left over from a build that once had it. Cython pools all
string constants, so its presence in the binary is not proof of an import.
Resolve during the Phase 1 oracle run, which will show whether importing
`explosionDamageManager` actually fails.

### 10. Two client modules cannot be parsed by Python 3 — OPEN

`aoslib/gui.py`, `aoslib/scenes/frontend/leaderboardListPanel.py`

Both are Python 2 source that raises `SyntaxError` under Python 3
(`Missing parentheses in call to 'print'`). They block the Python 3 migration
and are the reason for defect 11 below.

---

## Tests

### 11. Frontend tests extract methods by line-prefix string matching — OPEN

`tests/test_gui_scrollbar.py`, `tests/test_special_list_panel_layouts.py`

Because their target modules cannot be imported under Python 3 (defect 10),
these tests locate a method by matching a line prefix, slice it out of the
source, dedent it, and `exec` it against a fabricated globals dict that injects
`xrange` as a Python 2 shim.

It passes today, but any reformatting of those two files, or the introduction
of a Python 2-only construct inside an extracted method, breaks six tests in a
way that has nothing to do with the change that caused it. The workaround
should be deleted once defect 10 is fixed and the modules import normally.
