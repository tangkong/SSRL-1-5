"""
Miscellaneous devices
"""
__all__ = ['shutter', 'I1', 'I0', 'lrf',]

from ophyd import EpicsSignalRO, EpicsSignal

shutter = EpicsSignal('BL00:RIO.DO00', name='FastShutter')
I1 = EpicsSignalRO('BL00:RIO.AI2', name='I1')
I0 = EpicsSignalRO('BL00:RIO.AI1', name='I0')

lrf = EpicsSignalRO('BL00:RIO.AI0', name='lrf')