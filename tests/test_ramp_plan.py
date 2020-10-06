import databroker
from ophyd.sim import det, motor
from bluesky import RunEngine
from bluesky.plans import count, ramp_plan
from bluesky.plan_stubs import mvr, trigger_and_read

db = databroker.Broker.named('temp')
RE = RunEngine()
RE.subscribe(db.insert)

from ophyd import StatusBase

# go_plan
def kickoff():
    st = StatusBase()
    for i in range(20):
        yield from mvr(motor, -1)
        yield from mvr(motor, 1)
    return st

def inner_plan():
    yield from trigger_and_read([det])

# Final call
RE(ramp_plan(kickoff(), motor, inner_plan))


# def ramp_plan(go_plan, monitor_sig, inner_plan_func, 
# take_pre_data=True, timeout=None, period=None, md=None)
from databroker import Broker
from bluesky.plans import ramp_plan
from bluesky.plan_stubs import trigger_and_read
from bluesky import Msg
from bluesky.utils import RampFail
import numpy as np
import time

from ophyd.positioner import SoftPositioner
from ophyd import StatusBase
from ophyd.sim import SynGauss

tt = SoftPositioner(name='mot')
tt.set(0)
dd = SynGauss('det', tt, 'mot', 0, 3)

st = StatusBase()

def kickoff():
    yield Msg('null')
    for j, v in enumerate(np.linspace(-2, 2, 10)):
        RE.loop.call_later(.1 * j, lambda v=v: tt.set(v))
    RE.loop.call_later(1.2, st._finished)
    return st

def inner_plan():
    print(tt.position)
    yield from trigger_and_read([dd])


g = ramp_plan(kickoff(), tt, inner_plan, period=0.08)
db = Broker.named('temp')
from bluesky import RunEngine
RE = RunEngine()
RE.subscribe(db.insert)
rs_uid, = RE(g)