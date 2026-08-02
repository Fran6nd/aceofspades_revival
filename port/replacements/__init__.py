# -*- coding: utf-8 -*-
"""Native-Python replacements for the shipped extension modules.

One module per native module, named after it with dots flattened, so
`aoslib.scenes.main.player` becomes `aoslib_scenes_main_player`. The shim in
`port.native_modules` serves these under the original names when a module is
routed to the `replacement` backend.

`shared/steam.py` is the precedent for what one of these should look like: it
documents the source of the ABI it reproduces, states its compatibility, and is
honest about being a reconstruction rather than a byte-for-byte recreation.

Python compatibility: 2.7 and 3.x.
"""

from __future__ import absolute_import
