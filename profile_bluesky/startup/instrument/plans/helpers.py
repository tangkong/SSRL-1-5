""" 
Helper plans, functions
"""

from ..framework.initialize import db

from ..devices.stages import px,py,pz
from ..devices.misc_devices import filter1, filter2, filter3, filter4
from ..devices.xspress3 import xsp3

import bluesky.plans as bp
import bluesky.plan_stubs as bps

__all__ = ['filters', 'reset_offset', 'center', 'home_offsets',  
            'home', 'copper', 'calib', 'wafer1', 'wafer2', 
            'wmx','wmy', 'w1', 'w2']

def filters(new_vals=None):
    if new_vals:
        filter1.put(new_vals[0]*4.9)
        filter2.put(new_vals[1]*4.9)
        filter3.put(new_vals[2]*4.9)
        filter4.put(new_vals[3]*4.9)
    print(f'filter1: {filter1.get():.1f}')
    print(f'filter2: {filter2.get():.1f}')
    print(f'filter3: {filter3.get():.1f}')
    print(f'filter4: {filter4.get():.1f}')

# reset offsets
def reset_offset():
    px.user_offset.set(39)
    py.user_offset.set(-29.15)
    pz.user_offset.set(0.33)

# center the z position based on signal from the copper on xps3
def center(signal_key='xsp3_channel1_rois_roi01_value', motor_key='s_stage_pz'):
    # first move the stage to the copper
    yield from copper()

    # do a z-scan while reading the xps3
    num=10
    xsp3.total_points.put(num)
    yield from bp.rel_scan([xsp3],pz,-3,3,num=num)

    # grab the data to find the signal peak, no need to fill data, ROI's are scalars
    df = db[-1].table()
    ds = df[signal_key]
    dz = df[motor_key]

    # find the location of the signal maximum
    # need to check out the data type of the xps3
    deriv = ds.diff()/dz.diff()
    left_z = dz[deriv==deriv.max()].item()
    right_z = dz[deriv==deriv.min()].item()
    nz = (right_z-left_z)/2 + left_z
    print(f'({left_z}, {right_z})--> {nz}')
    # set the z offset so that the stage is zeroed at the signal max
    # user_readback=dial+offset
    curr_offset = pz.user_offset.get()
    pz.user_offset.set(curr_offset-nz)

    # move to the home location
    #yield from home()
    yield from bps.mv(px,0,py,0,pz,0)

# move to hardcoded positions 
def home_offsets():
    yield from bps.mv(px.user_offset, -5)
    yield from bps.mv(py.user_offset, -9.5)

def home():
    # move to 0,0 (assumes at the moment that offsets have not changed)
    #yield from home_offsets()
    yield from bps.mv(px,0)
    yield from bps.mv(py,0)

def copper():
    #yield from home_offsets()
    yield from bps.mv(px,-47.5)
    yield from bps.mv(py,12.5)

def calib():
    #yield from home_offsets()
    yield from bps.mv(px,34)
    yield from bps.mv(py,0)

def wafer1():
    yield from bps.mv(px,0)
    yield from bps.mv(py,-46)

def wafer2():
    yield from bps.mv(px,0)
    yield from bps.mv(py,46)

w1 = [0.0, -46.0]
w2 = [0.0, 46.0]

def wmx():
    return px.user_readback.get()

def wmy():
    return py.user_readback.get()