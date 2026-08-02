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
- [x] Record which modules import cleanly and which fail, with tracebacks
- [x] Isolate each probe in its own process so one crash does not end the run
- [x] Determine whether `shared.playerInteractions` is a live dependency or a
      dead reference — dead, `explosionDamageManager` imports without it
- [x] Assess whether rendering modules can be exercised with no GPU or display —
      six abort the interpreter and need static recovery instead

### 0.4 Module shim loader
- [x] Import hook that routes each native module to original or replacement
- [x] Per-module configuration switch
- [x] Verify the stock client is unaffected when all modules route to original
- [ ] Handle package `__init__` side effects, which run before the shim is
      consulted and fail off Windows

---

## Step 1 — API extraction

- [x] Harness that imports every native module and walks its object graph
- [x] Capture classes, bases, methods, and module constants
- [x] Capture signatures via `binding=True` introspection
- [x] Capture docstrings and the Cython `__test__` doctest table
- [x] Emit a typed API skeleton per module, committed as the reference
- [x] Probe for integrity checks that would reject replaced modules — none seen;
      every loadable module imported without complaint
- [x] Confirm whether `packet` contains more than protocol serialization — it
      does not; 139 packet classes, the rest is a re-exported constants namespace

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
- [x] Choose the target Python 3 minimum version — 3.9 or later, set by
      modern Twisted and pyglet 2.x; CI already uses 3.12
- [x] Decide how the 2.7 client stays buildable during the transition —
      straddle: every conversion stays valid in both 2.7 and 3.x

### 3.2 Conversion
- [x] Convert the syntax Python 3 cannot parse (30 files, all packages)
- [ ] Convert `shared/`
- [ ] Convert `aoslib/` pure-Python modules
- [ ] Convert `playlists/`
- [ ] Remove the method-slicing workaround in the tests once their targets parse
- [~] Replace the Python 2-era pinned dependencies with current releases —
      `toml` removed as unused; Twisted decision below

### 3.3 Twisted removal

Investigation: Twisted appears in 11 files and roughly 30 call sites, none of
them gameplay networking — that runs through `enet` and `aoslib.network`. Every
replacement already exists in the tree: `revival_http` for HTTP, `pyglet.clock`
for timers, stdlib `logging` for logs. `twisted.web.client.getPage`, used in
`customServerJoiner.py`, was removed from Twisted in 22.1.0.

`aoslib/pygletreactor.py` is the crux: it slaves Twisted's reactor to pyglet's
event loop at 10 Hz, depends on a private underscore module, and `local_host.py`
already documents it as unreliable. Removing Twisted deletes it outright rather
than porting it onto pyglet 2.x.

- [ ] Replace `deferToThread` in `aoslib/web.py` and `aoslib/scoremanager.py`
- [ ] Replace the Deferred wrapper around local file I/O in `aoslib/favourite.py`
- [ ] Replace `getPage` in `customServerJoiner.py` with `revival_http`
- [x] Remove the dead `getPage` import in `playlistServerJoiner.py`
- [ ] Replace `reactor.callLater` with `pyglet.clock.schedule_once`
- [ ] `playlistServerJoiner.py` still imports `reactor` without using it.
      Importing it *installs* the default reactor, which conflicts with
      `pygletreactor.install()` if this module is imported first — check the
      ordering as part of the reactor removal rather than in isolation
- [ ] Replace `twisted.python.log` with stdlib `logging`
- [ ] Delete `aoslib/pygletreactor.py` and its PyInstaller hook workaround
- [ ] Drop Twisted and zope.interface from `requirements.txt`

### 3.4 pyglet migration

The vendored `vendor/pyglet` is pyglet **1.2dev** as Python 2.7 bytecode with no
source, so moving off it is mandatory. The target is **1.5.27, not 2.x** — these
are separate projects and must not be conflated.

1.5.27 keeps `glext_arb.py` and `glu.py`, so all 863 GL references resolve
unchanged, and the client never uses `pyglet.text`, `pyglet.font`,
`pyglet.media` or `Batch` (font is native FTGL, audio is direct ctypes OpenAL).
That makes it a small hop.

It is also what makes native macOS possible at all: pyglet 1.5.27's Cocoa
backend requests a legacy OpenGL 2.1 profile, where the existing fixed-function
renderer and `#version 110` shaders run as-is. pyglet 2.0's Cocoa backend gives
a Core 3.2/4.1 profile, where fixed function does not exist.

- [ ] Move to pyglet 1.5.27 and drop the vendored bytecode
- [ ] Replace `pyglet.window.get_platform()` with `pyglet.canvas.get_display()`
- [ ] Fix `set_exclusive_keyboard()` being called before `Window.__init__`
- [ ] Delete `aoslib/pyglet_win32_raw_mouse.py` and its call site — pyglet has
      handled raw input natively since 1.5, and the patch already self-disables
      on anything other than 1.2. Must happen *with* the version bump, not
      before: on the current 1.2dev it is live and removing it early would lose
      raw mouse input
- [ ] Re-verify the `EventLoop` subclass and the `_event_stack` reordering in
      `aoslib/parachute_key_patch.py`
- [ ] Confirm `window.invalid` still paces frames under 1.5

### 3.4b pyglet 2.x — deferred, tracked separately

Not part of this migration. Roughly 12–26 person-weeks, and it is a renderer
rewrite rather than a port: 610 fixed-function call sites across 79 files, 51
shader sources at `#version 110` using built-ins deleted in GLSL 330, ARB
assembly programs with no core equivalent, and GL selection-buffer picking.

Worst failure mode to remember: `Texture.blit()` stops honouring the modelview
matrix and current colour, so 145 blit sites and every Sprite still compile and
run while drawing at the wrong position, scale and tint, with no exception.

Best merged with the `port/` reimplementation of `draw`, `mesh` and `kv6`, since
those must become modern GL regardless and doing both twice would be waste.

### 3.5 Validation
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
