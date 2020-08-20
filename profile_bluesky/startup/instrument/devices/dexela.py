from ophyd import EpicsSignal, Component as Cpt
from ophyd.signal import SignalRO
from ophyd import ADComponent as ADC
from ophyd.areadetector import cam
from ssrltools.devices.dexela import SSRLDexelaDet, DexelaTiffPlugin

from ..session_logs import logger
logger.info(__file__)

__all__ = ['dexDet', ]

class HackedCam(cam.DexelaDetectorCam):
    port_name = Cpt(SignalRO, value='DEX1')

class DexelaDet15(SSRLDexelaDet):
    """
    Final class for Dexela Detector on SSRL BL 1-5
    - add Plugins (TIFF plugin, etc)
    det = DexelaDet15(prefix, name='name')
    """
    # DexelaDetector from ophyd pulls in all Dexela specific PV's
    write_path = 'E:\\dexela_images\\'
    cam = ADC(HackedCam, '' ) #cam.DexelaDetectorCam, '') 
    # In case where TIFF plugin is being used
    tiff = Cpt(DexelaTiffPlugin, 'TIFF:',
                       read_attrs=[], configuration_attrs=[],
                       write_path_template=write_path,
                       read_path_template='/dexela_images/',
                       path_semantics='windows')
    # Else there should be an NDArrayData PV
    image = Cpt(EpicsSignal, 'IMAGE1:ArrayData')
    highest_pixel = Cpt(EpicsSignal, 'HighestPixel')

    def trigger(self):
        ret = super().trigger()
        self.cam.image_mode.put(0) # Set image mode to single...
        return ret
        
    # Could add more attributes to file_plugin
    # could add stage behavior


# Connect PV's to Ophyd objects

dexDet = DexelaDet15('SSRL:DEX2923:', name='dexela', 
                        read_attrs=['highest_pixel', 'tiff'])

dexDet.configuration_attrs.append('cam.num_images')