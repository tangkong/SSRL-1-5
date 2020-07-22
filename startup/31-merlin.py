from ophyd import Component as Cpt, Device, SingleTrigger
from ophyd.signal import EpicsSignal
from ophyd.areadetector import TIFFPlugin
from ophyd.areadetector.filestore_mixins import FileStoreTIFFIterativeWrite

print('-------------------31-merlin.py startup file')
class MerlinTiffPlugin(TIFFPlugin, FileStoreTIFFIterativeWrite):
    pass


#class SSRLMerlinDet(SingleTrigger, MerlinDetector):
#    pass


class Merlin15(SingleTrigger, Device):
    acquire = Cpt(EpicsSignal, 'Acquire')
    image = Cpt(EpicsSignal, 'IMAGE1:ArrayData')


merlinDet = Merlin15('SSRL:MERLIN:', name='merlin')
