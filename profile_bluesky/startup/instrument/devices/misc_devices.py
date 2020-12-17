"""
Miscellaneous devices
"""
__all__ = ['shutter', 'I1', 'I0', 'lrf', 'table_trigger', 'table_busy',
            'filter1', 'filter4']

from ophyd import EpicsSignalRO, EpicsSignal

shutter = EpicsSignal('BL00:RIO.DO00', name='FastShutter')
I1 = EpicsSignalRO('BL00:RIO.AI2', name='I1')
I0 = EpicsSignalRO('BL00:RIO.AI1', name='I0')

lrf = EpicsSignalRO('BL00:RIO.AI0', name='lrf')

table_trigger = EpicsSignal('BL00:RIO.DO01', name='tablev_scan trigger')
table_busy = EpicsSignalRO('BL00:RIO.AI3', name='tablev_scan busy')

filter1 = EpicsSignal('BL00:RIO.AO1', name='filter1') # high (4.9V) = filter out
filter2 = EpicsSignal('BL00:RIO.AO2', name='filter2') 
filter3 = EpicsSignal('BL00:RIO.AO3', name='filter3') 
filter4 = EpicsSignal('BL00:RIO.AO4', name='filter4') 