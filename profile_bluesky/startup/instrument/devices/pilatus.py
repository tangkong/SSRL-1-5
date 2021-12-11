from ophyd import SingleTrigger, Component as Cpt, ADComponent as ADC

from ophyd.areadetector.detectors import PilatusDetector
from ssrltools.devices.areadetectors import MarFileStoreTIFF
from ophyd.areadetector import cam

from ..session_logs import logger
logger.info(__file__)

__all__ = ['pilDet', ]


class PilDet15(SingleTrigger, PilatusDetector):
    """PilDet15 
    det = PilDet(prefix, name='name', read_attrs=['tiff'])
    """
    # file write path
    write_path = '/home/det/images/bluetest/'

    # no cam subdivision
    cam = ADC(cam.PilatusDetectorCam, '')

    tiff = Cpt(MarFileStoreTIFF, '', # Same slightly different structure as Mar
                write_path_template=write_path,
                read_path_template='/home/det/images/bluetest/', # same path but different fs
                path_semantics='posix') #, root='/home/data/')

    # image = ???  Array data PV?
pilDet = PilDet15('BL15:PILATUS1M:', name='pilatus1M', read_attrs=['tiff'])
