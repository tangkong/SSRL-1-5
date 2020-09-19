from ophyd import SingleTrigger, Component as Cpt, ADComponent as ADC

from ophyd.areadetector.detectors import MarCCDDetector
from ssrltools.devices.areadetectors import MarTiffFakePlugin, MarFileStoreTIFF
from ophyd.areadetector import cam

from ..session_logs import logger
logger.info(__file__)

__all__ = ['marDet', ]


class MarCCDDet15(SingleTrigger, MarCCDDetector):
    """MarCCDDet15 
    det = MarCCDDet15(prefix, name='name', read_attrs=['tiff'])
    """
    # file write path
    write_path = '/tmp/marccd/'

    # no cam subdivision
    cam = ADC(cam.MarCCDDetectorCam, '')

    tiff = Cpt(MarFileStoreTIFF, '', 
                write_path_template=write_path,
                read_path_template='/home/b_spec/data/marCCD/',
                path_semantics='posix')

marDet = MarCCDDet15('BL15:MARCCD:', name='marCCD', read_attrs=['tiff'])