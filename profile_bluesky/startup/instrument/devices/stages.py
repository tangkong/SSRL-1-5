"""
stages 
"""

__all__ = ['s_stage',]

from ..framework import sd
from ..session_logs import logger
logger.info(__file__)

from ophyd import Component as Cpt, MotorBundle, EpicsMotor

class HiTpStage(MotorBundle):
    """HiTp Sample Stage"""
    #stage x, y
    px = Cpt(EpicsMotor, 'BL00:IMS:MOTOR3', kind='hinted', labels=('sample',))
    py = Cpt(EpicsMotor, 'BL00:IMS:MOTOR4', kind='hinted', labels=('sample',))
    pz = Cpt(EpicsMotor, 'BL00:IMS:MOTOR2', kind='hinted', labels=('sample',))

    # plate vert adjust motor 1, 2
    vx = Cpt(EpicsMotor, 'BL00:PICOD1:MOTOR3', labels=('sample',))
    vy = Cpt(EpicsMotor, 'BL00:PICOD1:MOTOR2', labels=('sample',))

    th = Cpt(EpicsMotor, 'BL00:IMS:MOTOR1', labels=('sample',))

s_stage = HiTpStage('', name='s_stage')

# measure stage status at beginning of every plan
sd.baseline.append(s_stage)