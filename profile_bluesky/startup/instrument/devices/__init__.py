"""
Device import file. To disable a device in Bluesky, simply comment out the line.

Typically one of {dexela, marCCD, pilatus} will be enabled at a time.
"""

from .stages import *
from .xspress3 import *
# from .dexela import *
from .marCCD import *
# from .pilatus import *
from .misc_devices import *