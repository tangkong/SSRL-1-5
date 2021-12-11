"""
Plans for more automated optimization acquisition plans, w.r.t area detectors
"""
import numpy as np
import pandas as pd

import bluesky.plan_stubs as bps
import bluesky.plans as bp
from bluesky_live.bluesky_run import BlueskyRun, DocumentCache

from ..framework import db
from ..devices.misc_devices import filter1, filter2, filter3, filter4
from .helpers import home

__all__ = ['align_wafer','filter_opt_count', 'solve_filter_setup','filter_thicks', 'filter_hist']

# dataframe to record intensity and filter information.  
filter_hist = pd.DataFrame(columns=['time','filter_i','filter_f','I_i', 'I_f', 
                                    'I_f/I_i', 'mu', 'signal'])

filter_thicks = [0.89, 2.52, 3.83, 10.87]

def align_wafer(xsp3,px,py,*,md=None):
    """
    find the x and y boundaries of a combinatorial wafer library (of either 3in or 4in diameter), find the middle of the wafer, and set motor offsets to center the wafer at (0,0)

    :param xsp3: xpress3 vortex detector
    :type xsp3:
    :param px: x motor object
    :type px:
    :param py: y motor object 
    :type py:
    
    """

    # first move the stage to whatever 'home' currently is
    #yield from home()

    # just assume you need to take as wide of a scan as possible
    xtens = 43
    num = 60
    
    for mot in [px, py]:
        # take a rel_scan in the x direction, read the xpress3 total signal, and find the sample boundaries
        # take derivative and find maxes?
        yield from bp.rel_scan([xsp3],mot,-xtens,xtens,num=num,md=md)

        

        # okay now grab the data from the correct roi
        xsignal = np.array(db[-1].table()['xsp3_channel1_rois_roi02_value'])
        print(xsignal)
        xpos = np.array(db[-1].table()[mot.name]) # might work with [mot.name]
        print(xpos)
        # take the derivative and find the highest two points
        # we have to pad a value to the beginning/end of deriv
        # so that it has the same dimension as the position/signal arrays
        # padding the front with a 0 seems to work (?tbd)
        deriv_x = np.diff(xsignal,prepend=0)/np.diff(xpos,prepend=0)


        left_x = xpos[deriv_x==deriv_x.max()].item()
        right_x = xpos[deriv_x==deriv_x.min()].item()
        nx = (right_x-left_x)/2 + left_x

        # get the current position and adjust by nx
        cpos = mot.user_offset.get()
        mot.user_offset.set(cpos-nx) #subtract? add? signed or abs val?


    # move to the center of the sample at the end
    yield from bps.mv(px,0,py,0)

def max_pixel_count(dets, sat_count=60000, md={}):
    """max_pixel_count 

    Adjust acquisition time based on max pixel count
    Assume each det in dets has an attribute det.max_count.
    Assume counts are linear with time. 
    Scale acquisition time to make det.max_count.get()=sat_count
    """

    for det in dets:
        yield from bps.stage(det)
        yield from bps.trigger_and_read(det)
        curr_acq_time = det.cam.acquire_time.get()
        # =================== BIG IF, DOES THIS EXIST
        curr_max_counts = det.max_count.get()
        # ============================================
        new_acq_time = round(sat_count / curr_max_counts * curr_acquire_time, 2)
        
        yield from bps.mv(det.cam.acquire_time, new_acq_time)

    # run standard count plan with new acquire times
    yield from bp.count(dets, md=md)

def filter_opt_count(det, target_count=100000, mu=0.8, md={}):
    """ filter_opt_count
    OPtimize counts using filters 
    Assumes mu=0.2, x = [0.89, 2.52, 3.83, 10.87]
    I = I_o \exp(-mu*x) 

    Only takes one detector, since we are optimizing based on it alone
    target is mean+2std
    """
    dc = DocumentCache()
    token = yield from bps.subscribe('all', dc)
    yield from bps.stage(det)

    md = {}
    
    yield from bps.open_run(md=md)    
    # BlueskyRun object allows interaction with documents similar to db.v2, 
    # but documents are in memory
    run = BlueskyRun(dc)
    yield from bps.trigger_and_read([det, filter1, filter2, filter3, filter4])

    data = run.primary.read()['pilatus300k_image']
    mean = data[-1].mean().values.item() # xarray.DataArray methods
    std = data[-1].std().values.item() # xarray.DataArray methods
    curr_counts = mean + 2*std


    # gather filter information and solve 
    filter_status = [round(filter1.get()/5), round(filter2.get()/5), 
                        round(filter3.get()/5), round(filter4.get()/5)]
    print(filter_status)
    filter_status = [not e for e in filter_status]
    new_filters = solve_filter_setup(filter_status, curr_counts, target_count, mu=mu)
    # invert again to reflect filter status
    new_filters = [not e for e in new_filters]
    print(new_filters)
    # set new filters and read.  For some reason hangs on bps.mv when going high
    filter1.put(new_filters[0]*4.9)
    filter2.put(new_filters[1]*4.9)
    filter3.put(new_filters[2]*4.9)
    filter4.put(new_filters[3]*4.9)
    
    yield from bps.trigger_and_read([det, filter1, filter2, filter3, filter4])

    # close out run
    yield from bps.close_run()
    yield from bps.unsubscribe(token)
    yield from bps.unstage(det)


def solve_filter_setup(curr_filters, curr_counts, target_counts, 
                        x=filter_thicks, mu=0.2):
    """solve_filter_setup 
    
    Return filter setup given filter thicknesses (x), and attenuation coeff (mu)
    curr_filters: boolean array

    Operates with 1 = filter in
    ... boolean values are flipped.  signal: 1=filter out, math: 1=filter in
    """
    # get I_o from detector
    x_curr = np.dot(curr_filters, x)
    I0 = curr_counts / np.exp(-mu * x_curr)

    # solve for desired x
    x_new = -np.log(target_counts / I0) / mu

    # return closest arrangement of filters
    # due to small number of possible combinations, can just enumerate
    # max=2^4-1=15

    filter_cfgs = list(range(16))
    filter_cfgs = [int_to_bool_list(k) for k in filter_cfgs]

    I_new = [I0*np.exp(-mu * np.dot(x, k)) for k in filter_cfgs]
    print(I_new)
    index = np.argmin(np.abs(np.array(I_new)-target_counts))

    return filter_cfgs[index]

def int_to_bool_list(num):
    """int_to_bool_list 
    credits to https://stackoverflow.com/questions/33608280/convert-4-bit-integer-into-boolean-list
    """
    bin_string = format(num, '04b')
    return [x=='1' for x in bin_string[::-1]]


def opt_filters():
    """
    make decorator? or just run as plan prior to each collection? 
    """


    pass

def solve_mu(hist=filter_hist):
    """
    Return average mu from most recent hour of measurements?  
    ? how to account for filter box changes?  Zero out measurements?  

    --> assume all measurements are from same filter box, shouldn't see any big jumps
    """
    
    mu = hist['mu'].mean()

    if mu is np.nan:
        raise ValueError('no measurements taken with current filters')
    
    return mu



def SNR_opt():
    """ ???? Maybe?
    """
