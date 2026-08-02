# Native Module API Reference

Captured by importing the shipped extension modules under 32-bit
Python 2.7 on Windows, which is the only place they load. Generated;
do not edit by hand.

- interpreter: `2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:19:08) [MSC v.1500 32 bit (Intel)]`
- pointer width: 32-bit

| module | status | members |
| --- | --- | --- |
| `aoslib.character` | crashed | 0 |
| [`aoslib.customimage`](aoslib.customimage.pyi) | package | 2 |
| `aoslib.draw` | crashed | 0 |
| [`aoslib.font`](aoslib.font.pyi) | package | 27 |
| `aoslib.gamemanager` | crashed | 0 |
| [`aoslib.gl`](aoslib.gl.pyi) | package | 5 |
| `aoslib.hud.hud` | crashed | 0 |
| [`aoslib.kv6`](aoslib.kv6.pyi) | package | 11 |
| [`aoslib.mesh`](aoslib.mesh.pyi) | package | 2 |
| [`aoslib.network`](aoslib.network.pyi) | package | 49 |
| [`aoslib.physfs`](aoslib.physfs.pyi) | package | 11 |
| `aoslib.scenes.main.gameScene` | crashed | 0 |
| `aoslib.scenes.main.player` | crashed | 0 |
| [`aoslib.ugc_data`](aoslib.ugc_data.pyi) | package | 502 |
| [`aoslib.vxl`](aoslib.vxl.pyi) | package | 5600 |
| [`aoslib.world`](aoslib.world.pyi) | package | 5598 |
| [`shared.bytes`](shared.bytes.pyi) | package | 3 |
| [`shared.common`](shared.common.pyi) | package | 5632 |
| [`shared.explosionDamageManager`](shared.explosionDamageManager.pyi) | package | 5588 |
| [`shared.glm`](shared.glm.pyi) | package | 4 |
| [`shared.lzf`](shared.lzf.pyi) | package | 3 |
| [`shared.packet`](shared.packet.pyi) | package | 5722 |
| [`shared.shrapnelManager`](shared.shrapnelManager.pyi) | package | 5584 |

## Modules that abort the interpreter

These terminate the process rather than raising, so they cannot be
introspected on a runner with no GPU or display. Their API has to be
recovered statically instead.

- `aoslib.character`
- `aoslib.draw`
- `aoslib.gamemanager`
- `aoslib.hud.hud`
- `aoslib.scenes.main.gameScene`
- `aoslib.scenes.main.player`
