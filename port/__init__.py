# -*- coding: utf-8 -*-
"""Support code for the native module port.

Nothing here is part of the shipped client. It exists to make the replacement
of the Windows-only native extension modules incremental and measurable.

Python compatibility: 2.7 and 3.x. The 2.7 half is needed because the original
modules can only be loaded by that interpreter, and is not new client code.
"""

from __future__ import absolute_import
