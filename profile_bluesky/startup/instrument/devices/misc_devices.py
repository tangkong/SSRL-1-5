"""
Miscellaneous devices
"""
__all__ = ['shutter', 'I1', 'I0', 'lrf', 'table_trigger', 'table_busy',
            'filter1', 'filter2', 'filter3', 'filter4']

from ophyd import EpicsSignalRO, EpicsSignal

shutter = EpicsSignal('HITP:RIO.DO00', name='FastShutter')
I1 = EpicsSignalRO('HITP:RIO.AI2', name='I1')
I0 = EpicsSignalRO('HITP:RIO.AI1', name='I0')

lrf = EpicsSignalRO('HITP:RIO.AI0', name='lrf')

table_trigger = EpicsSignal('HITP:RIO.DO01', name='tablev_scan trigger')
table_busy = EpicsSignalRO('HITP:RIO.AI3', name='tablev_scan busy')

filter1 = EpicsSignal('HITP:RIO.AO1', name='filter1') # high (4.9V) = filter out
filter2 = EpicsSignal('HITP:RIO.AO2', name='filter2') 
filter3 = EpicsSignal('HITP:RIO.AO3', name='filter3') 
filter4 = EpicsSignal('HITP:RIO.AO4', name='filter4') 
