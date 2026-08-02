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
- [ ] Verify the workflows on a real push and fix what breaks
- [ ] Decide whether to pin UPX, which currently makes CI and local artifact
      checksums differ
- [ ] Add integrity hashes for the 5 toolchain archives fetched without
      verification

### 0.3 Windows oracle harness
- [ ] CI job that provisions 32-bit Python 2.7 purely for module inspection
- [ ] Confirm every native module imports cleanly in that job
- [ ] Establish how results are published as artifacts and reviewed natively
- [ ] Assess whether rendering modules can be exercised on a runner with no GPU
      or display, and record the fallback if not

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
