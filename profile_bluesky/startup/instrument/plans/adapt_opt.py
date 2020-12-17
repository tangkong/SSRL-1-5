"""
Plans for more automated optimization acquisition plans, w.r.t area detectors
"""
import numpy as np
import pandas as pd

import bluesky.plan_stubs as bps
import bluesky.plans as bp
from bluesky_live.bluesky_run import BlueskyRun, DocumentCache

from ..devices.misc_devices import filter1, filter2, filter3, filter4


__all__ = ['filter_opt_count', 'solve_filter_setup','filter_thicks', 'filter_hist']

# dataframe to record intensity and filter information.  
filter_hist = pd.DataFrame(columns=['time','filter_i','filter_f','I_i', 'I_f', 
                                    'I_f/I_i', 'mu', 'signal'])

filter_thicks = [0.89, 2.52, 3.83, 10.87]

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

def filter_opt_count(det, sat_count=60000, md={}):
    """ filter_opt_count
    OPtimize counts using filters 
    Assumes mu=0.2, x = [0.89, 2.52, 3.83, 10.87]
    I = I_o \exp(-mu*x) 

    Only takes one detector, since we are optimizing based on it alone
    """
    dc = DocumentCache()
    token = yield from bps.subscribe('all', dc)
    yield from bps.stage(det)

    md = {}
    
    yield from open_run(md=md)    
    # BlueskyRun object allows interaction with documents similar to db.v2, 
    # but documents are in memory
    run = BlueskyRun(dc)
    yield from bps.trigger_and_read([det])

    data = run.primary.read()['pilatus300k_image']
    curr_counts = data[-1].max().valuese.item() # xarray.DataArray methods
    
    # gather filter information and solve 
    filter_status = [int(filter1.get()/5), int(filter2.get()/5), 
                        int(filter3.get()/5), int(filter4.get()/5)]
    print(filter_status)
    filter_status = [not e for e in filter_status]
    new_filters = solve_filter_setup(filter_status, curr_counts, sat_count)
    # invert again to reflect filter status
    new_filters = [not e for e in new_filters]
    print(new_filters)
    # set new filters and read 
    yield from bps.mv(filter1, new_filters[0]*4.9)
    yield from bps.mv(filter2, new_filters[1]*4.9)
    yield from bps.mv(filter3, new_filters[2]*4.9)
    yield from bps.mv(filter4, new_filters[3]*4.9)

    yield from bp.trigger_and_read([det, filter1, filter2, filter3, filter4])

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