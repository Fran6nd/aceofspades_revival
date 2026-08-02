# Cross-Platform Port — Task List

Native macOS and Linux support for the client. Tracked step by step; each step
is investigated first, then executed, then committed.

Two hard constraints:

- **Native only.** No Wine, no Proton, no compatibility layer. Original module
  behaviour is observed on a real Windows CI runner instead.
- **Python 3 only.** No new Python 2.7 code. 2.7 survives solely as a capture
  tool on the Windows runner, because the original modules link against
  `python27.dll`.

Legend: `[ ]` pending · `[x]` done · `[~]` in progress · `[!]` blocked

---

## Step 0 — Infrastructure

### 0.1 Planning and tracking
- [x] Start `BUGS.md` and fix defects on sight rather than accumulating them
- [x] Reconnaissance of all 24 native modules (toolchain, sources, classification)
- [x] Write the port plan working document
- [x] Create this task list

### 0.2 Continuous integration
- [x] Investigate release-build prerequisites for a clean runner
- [x] Investigate which tests can run, and on which platforms
- [x] Add `--skip-server` to the release builder so it can run without the
      BattleSpades repo checked out
- [x] Add the Windows release build workflow
- [x] Add the cross-platform test workflow (Linux, Windows, macOS)
- [x] Structure the build workflow as a platform matrix so macOS and Linux can
      be enabled later without a rewrite
- [x] Pin integrity hashes for the 5 toolchain archives that were fetched
      without verification, and make a missing hash a hard error
- [x] Disable UPX compression, which made build output depend on whether the
      machine had UPX installed and worked against the existing effort to
      avoid antivirus false positives
- [x] Cover both of the above with tests
- [~] Verify the workflows on a real run and fix what breaks

### 0.3 Windows oracle harness

Investigation findings:

- `import aoslib` runs `import aoslib.font` and `aoslib.graphicsManager`, and
  `import shared` runs `import shared.bytes, shared.packet`. No native module
  can be imported through its package without those side effects, so the
  harness must also try loading each `.pyd` in isolation.
- `graphicsManager` is inert at import time. `font` is a native module and is
  the only hazard in the `aoslib` package init.
- 43 distinct `aoslib.*` / `shared.*` names appear in the binaries. Exactly one,
  `shared.playerInteractions`, does not exist in the repo — referenced by
  `explosionDamageManager`.
- Six modules reference pyglet (`character`, `gamemanager`, `hud`, `gameScene`,
  `ugc_data`, `vxl`) and `gamemanager` also references Twisted, so both must be
  importable before those are attempted.
- Name references in a binary are not proof of an import at module-init time;
  Cython pools all string constants. The real import behaviour has to be
  measured on the runner rather than inferred here.

Tasks:

- [x] Map inter-module references and identify dependency-ordered leaves
- [x] Determine what the package `__init__` files do on import
- [x] Write the introspection harness (Python 2.7 compatible)
- [x] Add the CI job that provisions 32-bit Python 2.7 for inspection only
- [ ] Record which modules import cleanly and which fail, with tracebacks
- [ ] Determine whether `shared.playerInteractions` is a live dependency or a
      dead reference
- [ ] Assess whether rendering modules can be exercised with no GPU or display,
      and record the fallback if not

### 0.4 Module shim loader
- [ ] Import hook that routes each native module to original or replacement
- [ ] Per-module configuration switch
- [ ] Verify the stock client is unaffected when all modules route to original

---

## Step 1 — API extraction

- [ ] Harness that imports every native module and walks its object graph
- [ ] Capture classes, bases, methods, and module constants
- [ ] Capture signatures via `binding=True` introspection
- [ ] Capture docstrings and the Cython `__test__` doctest table
- [ ] Emit a typed API skeleton per module, committed as the reference
- [ ] Probe for integrity checks that would reject replaced modules
- [ ] Confirm whether `packet` contains more than protocol serialization

---

## Step 2 — Behavioral corpus

- [ ] Tracer wrapping every extracted entry point
- [ ] Scripted scenario drivers, since interactive play is unavailable in CI
- [ ] Cover all game modes, weapons, tutorial, and UGC paths
- [ ] Serialize argument and return traces to a replayable corpus
- [ ] Differential test runner that replays a corpus against any implementation

---

## Step 3 — Python 3 migration of the portable layer

Runs in parallel with Steps 1 and 2. The existing test suite is already Python 3
and already passes on all three platforms, so the harness exists up front.

### 3.1 Assessment
- [ ] Inventory every `.py` file by Python 2 vs 3 compatibility
- [ ] Identify files Python 3 cannot currently parse, starting with
      `aoslib/gui.py` and `aoslib/scenes/frontend/leaderboardListPanel.py`
- [ ] Choose the target Python 3 minimum version
- [ ] Decide how the 2.7 client stays buildable during the transition

### 3.2 Conversion
- [ ] Convert the standalone root modules
- [ ] Convert `shared/`
- [ ] Convert `aoslib/` pure-Python modules
- [ ] Convert `playlists/`
- [ ] Remove the method-slicing workaround in the tests once their targets parse
- [ ] Replace the Python 2-era pinned dependencies with current releases

### 3.3 pyglet migration
- [ ] Scope the move from the vendored 1.2dev bytecode to a maintained pyglet
- [ ] Map every pyglet API the client uses to its modern equivalent
- [ ] Port windowing, GL context handling, and batched graphics
- [ ] Replace the raw-mouse compatibility patch with a supported input path

### 3.4 Validation
- [ ] Extend the test suite to cover converted modules
- [ ] Keep all three platforms green throughout

---

## Step 4 — Quick wins (hand-written C and open-source modules)

Written directly in Python 3.

- [ ] `shared/lzf` — replace with LibLZF
- [ ] `shared/glm` — reimplement vector/matrix math
- [ ] `shared/bytes` — reimplement byte reader/writer
- [ ] `aoslib/mesh` — reimplement
- [ ] `enet` — rebuild the binding from upstream source
- [ ] `aoslib/physfs` — rebind against PhysicsFS
- [ ] `shared/packet` — reimplement from the published protocol documentation
- [ ] `shared/shrapnelManager` — reimplement
- [ ] `shared/explosionDamageManager` — reimplement
- [ ] `shared/common` — reimplement
- [ ] Validate each against the Step 2 corpus

---

## Step 5 — Decompilation tooling

- [ ] Extract Cython string constant tables as anchors
- [ ] Extract closure scope-struct names to recover function names
- [ ] Ghidra project with MSVC 2008 signatures applied
- [ ] Pattern library for Cython's generated code shapes
- [ ] Lifter producing Python 2 source from matched patterns
- [ ] Known-answer test: recover `scoremanager` from `gamemanager` and diff
      against the existing source copy
- [ ] Feed lifter output through the Step 3 conversion rules
- [ ] Measure recovery accuracy and iterate

---

## Step 6 — Bulk source recovery

- [ ] `gamemanager` — 4 bundled modules
- [ ] `hud` — 12 bundled modules
- [ ] `gameScene` — 40 bundled entity modules
- [ ] `font` — constants module
- [ ] Validate each recovered module against the corpus

---

## Step 7 — Engine modules

- [ ] `world` — physics
- [ ] `vxl` — voxel map rendering
- [ ] `kv6` — voxel model loading
- [ ] `character` — animation
- [ ] `draw` — 2D drawing
- [ ] `font` — text rendering
- [ ] `network` — transport
- [ ] `player`, `gameScene`, `ugc_data`, `customimage`, `gl` — remaining
- [ ] Converge the Python 3 tree with the retired 2.7 client and launch it

---

## Step 8 — Native platform support and release

### 8.1 Remaining platform work
- [ ] Replace the Windows API calls in `launcher.py` with portable equivalents
- [ ] Replace DPAPI credential storage with Keychain and libsecret backends
- [ ] Portable atomic file replacement in `display_config.py`
- [ ] Make the updater cross-platform
- [ ] Cross-platform local server launching in `local_host.py`
- [ ] Audit asset references for case-sensitivity against the real trees
- [ ] Verify OpenAL, ALURE, GLEW, and PhysicsFS availability per platform

### 8.2 Release
- [ ] Enable the macOS build job
- [ ] Enable the Linux build job
- [ ] Package a macOS bundle
- [ ] Package a Linux distributable
- [ ] Smoke-test native builds on both platforms
