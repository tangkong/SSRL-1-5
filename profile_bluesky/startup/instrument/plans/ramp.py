from ..framework import db, RE
from ..devices import s_stage

import bluesky.plans as bp
import bluesky.plan_stubs as bps 
import bluesky.preprocessors as bpp
from bluesky import Msg
from ophyd import StatusBase
import numpy as np

# wiggle scan for collecting LaB6 calibrant data.  
# goal: initiate collection and move motor back and forth 1mm

def wiggle_plan(dets, motor, delta, *, md=None):
    '''
    dets, a list of detectors to read, must have det.cam.acquire_time attribute
    delta, relative range to wiggle
    move through range in 5 step
    '''

    original_pos = motor.position()
    st = StatusBase()
    def kickoff(): # plan for moving 
        yield Msg('null') # ???
        # move once every second for 2 min
        for i in range(24): # 24*5 = 120
            for loc in np.linspace(-delta/2, delta/2, 5): # 5s, 
                RE.loop.call_later(1, lambda v=loc: motor.set(v))
        return st

    def inner_plan():
        yield from bps.trigger_and_read(dets)

    def clean_up():
        yield from bps.mv(motor, original_pos)

    timeout = dets[0].cam.acquire_time.value

    rp = bp.ramp_plan(kickoff(), motor, inner_plan, 
                            timeout=timeout,
                            md=md)

    return (yield from bpp.finalize_wrapper(rp, clean_up()))
