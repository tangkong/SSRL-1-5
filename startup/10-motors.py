# Instantiate ophyd motor classes
from ophyd import EpicsMotor, Device, Component as Cpt

#stage x, y
stage_x = EpicsMotor('', name='stage_x')
stage_y = EpicsMotor('', name='stage_y')

# plate vert adjust motor 1, 2
plate_x = EpicsMotor('', name='vert_x')
plate_y = EpicsMotor('', name='vert_y')
# Laser range finder?

# -----------------------------------------------------
# Eventually.... beamline/hutch controls

# mono

# slits 