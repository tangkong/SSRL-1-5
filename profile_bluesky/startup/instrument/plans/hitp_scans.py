""" 
scans for high throughput stage
"""

from .locs import loc177
from ..devices.stages import s_stage, px,py
from ..devices.xspress3 import xsp3
from ..devices.pilatus import pilDet
from ..devices.misc_devices import shutter as fs, lrf, I0, I1, table_busy, table_trigger
from ..framework import db
from .adapt_opt import align_wafer
from .helpers import home,wafer1,wafer2

import time 
import matplotlib.pyplot as plt
import numpy as np
import bluesky.plans as bp
from bluesky.preprocessors import inject_md_decorator 
import bluesky.plan_stubs as bps
from ssrltools.plans import meshcirc, nscan, level_stage_single

__all__ = ['opt_two_wafer','yale_fourin','loc_177_scan', 'loc_cust_scan', 'dark_light_plan', 'exp_time_plan', 'gather_plot_ims',
            'plot_dark_corrected', 'multi_acquire_plan', 'level_stage_single','level_s_stage','rand_exp_test' ]

# scan sample locations
@inject_md_decorator({'macro_name': 'loc_177_scan'})
def loc_177_scan(dets, skip=0, md={}):
    """loc_177_scan scans across a library with 177 points, measuring each 
    detector in dets

    :param dets: detectors to be 
    :type dets: list
    :param skip: number of data points to skip
    :yield: things from list_scan
    :rtype: Msg
    """
    # format locations and stage motors
    #if I0 not in dets:
    #    dets.append(I0)
    #if I1 not in dets:
    #    dets.append(I1)

    if xsp3 in dets:
        yield from bps.mv(xsp3.total_points, 177)

    # inject logic via per_step 
    class stateful_per_step:
        
        def __init__(self, skip):
            self.skip = skip
            self.cnt = 0
            #print(self.skip, self.cnt)

        def __call__(self, detectors, step, pos_cache):
            """
            has signature of bps.one_and_step, but with added logic of skipping 
            a point if it is outside of provided radius
            """
            if self.cnt < self.skip: # if not enough skipped
                self.cnt += 1
                pass
            else:
                yield from bps.one_nd_step(detectors, step, pos_cache)

    per_stepper = stateful_per_step(skip)

    yield from bp.list_scan(dets, s_stage.px, list(loc177[0]), 
                                s_stage.py, list(loc177[1]), 
                                per_step=per_stepper, md=md)


@inject_md_decorator({'macro_name': 'loc_cust_scan'})
def loc_cust_scan(dets, cust_locs, skip=0, md={}):
    """loc_cust_scan scans across a library with 177 points, measuring each 
    detector in dets

    :param dets: detectors to be 
    :type dets: list
    :param cust_locs: (2, N) array denoting N locations to scan.  First list 
                      will direct px and the second will direct py 
    :type cust_locs: list
    :param skip: number of data points to skip
    :yield: things from list_scan
    :rtype: Msg
    """
    # format locations and stage motors
    if I0 not in dets:
        dets.append(I0)
    if I1 not in dets:
        dets.append(I1)

    if xsp3 in dets:
        yield from bps.mv(xsp3.total_points, len(cust_locs[0]))

    # inject logic via per_step 
    class stateful_per_step:
        
        def __init__(self, skip):
            self.skip = skip
            self.cnt = 0
            #print(self.skip, self.cnt)

        def __call__(self, detectors, step, pos_cache):
            """
            has signature of bps.one_and_step, but with added logic of skipping 
            a point if it is outside of provided radius
            """
            if self.cnt < self.skip: # if not enough skipped
                self.cnt += 1
                pass
            else:
                yield from bps.one_nd_step(detectors, step, pos_cache)

    per_stepper = stateful_per_step(skip)

    yield from bp.list_scan(dets, s_stage.px, list(cust_locs[0]), 
                                s_stage.py, list(cust_locs[1]), 
                                per_step=per_stepper, md=md)

# collection plans
# Basic dark > light collection plan
@inject_md_decorator({'macro_name':'dark_light_plan'})
def dark_light_plan(dets, shutter=fs, md={}):
    '''
        Simple acquisition plan:
        - Close shutter, take image, open shutter, take image, close shutter
        dets : detectors to read from
        motors : motors to take readings from (not fully implemented yet)
        fs : Fast shutter, high is closed
        sample_name : the sample name
        Example usage:
        >>> RE(dark_light_plan())
    '''
    if I0 not in dets:
        dets.append(I0)
    if I1 not in dets:
        dets.append(I1)

    start_time = time.time()
    uids = []

    #close fast shutter, take a dark
    yield from bps.mv(fs, 1)
    mdd = md.copy()
    mdd.update(im_type='dark')
    uid = yield from bp.count(dets, md=mdd)
    uids.append(uid)


    # open fast shutter, take light
    yield from bps.mv(fs, 0)
    mdl = md.copy()
    mdl.update(im_type='primary')
    uid = yield from bp.count(dets, md=mdl)
    uids.append(uid)

    end_time = time.time()
    print(f'Duration: {end_time - start_time:.3f} sec')

    plot_dark_corrected(db[uids])

    return(uids)


# Plan for meshgrid + dark/light?...

# image time series
@inject_md_decorator({'macro_name':'exposure_time_series'})
def exp_time_plan(det, timeList=[1]):
    '''
    Run count with each exposure time in time list.  
    Specific to Dexela Detector, only run with single detector
    return uids from each count

    # TO-DO: Fix so both are under the same start document
    '''
    primary_det = det
    dets = []
    if I0 not in dets:
        dets.append(I0)
    if I1 not in dets:
        dets.append(I1)

    dets.append(primary_det)
    md = {'acquire_time': 0, 'plan_name': 'exp_time_plan'}
    uids = []
    for time in timeList:
        # set acquire time
        yield from bps.mov(primary_det.cam.acquire_time, time)
        md['acquire_time'] = time
        uid = yield from bp.count(dets, md=md)

        yield from bps.sleep(1)
        uids.append(uid)
   
    return uids

#helper functions, probably should go in a separate file

import datetime
fts = datetime.datetime.fromtimestamp
def gather_plot_ims(hdrs):
    '''
    helper function for plotting images. 
    '''
    plots=[]
    times=[]
    # gather arrs from db
    for hdr in hdrs:
        arr = hdr.table(fill=True)['dexela_image'][1]
        plots.append(arr)
        time = hdr.start['time']
        times.append(time)
        

    global curr_pos
    curr_pos = 0
    # Register key event
    def key_event(e): 
        global curr_pos 
        if e.key == 'right': 
            curr_pos=curr_pos + 1 
        elif e.key == 'left': 
            curr_pos = curr_pos - 1  
        else: 
            return 
        curr_pos = curr_pos % len(plots) 
        ax.cla()
        curr_arr = plots[curr_pos]
        ax.imshow(curr_arr, vmax=curr_arr.mean() + 3*curr_arr.std()) 

        dt = fts(times[curr_pos])
        ax.set_title(f'{dt.month}/{dt.day}, {dt.hour}:{dt.minute}')
        fig.canvas.draw() 

    fig = plt.figure()
    fig.canvas.mpl_connect('key_press_event', key_event)
    ax = fig.add_subplot(111)
    ax.imshow(plots[0], vmax=plots[0].mean() + 3*plots[0].std())
    dt = fts(times[0])
    ax.set_title(f'{dt.month}/{dt.day}, {dt.hour}:{dt.minute}')

    plt.show()


def plot_dark_corrected(hdrs):
    '''
    looks for name='dark' or 'primary'
    otherwise assumes dark comes first?
    '''

    for hdr in hdrs:
        if hdr.start['im_type']=='dark':
            darkarr = hdr.table(fill=True)['dexela_image'][1]
        elif hdr.start['im_type'] == 'primary':
            lightarr = hdr.table(fill=True)['dexela_image'][1]
        else:
            print('mislabeled data... ignoring for now')

    bkgd_subbed = lightarr.astype(int) - darkarr.astype(int)
    bkgd_subbed[ bkgd_subbed < 0 ] = 0
    plt.imshow(bkgd_subbed, vmax = bkgd_subbed.mean() + 3*bkgd_subbed.std())

def plot_MCA(hdrs):
    '''Plot MCA's from given hdr
    '''
    plt.figure()
    data = hdrs.table(fill=True)['xsp3_channel1'][1]

    plt.plot(data)
    plt.xlabel('Energy (keV)')
    plt.ylabel('Total counts')

@inject_md_decorator({'macro_name':'multi_acquire_plan'})
def multi_acquire_plan(det, acq_time, reps): 
    '''multiple acquisition run.  Single dark image, multiple light
    '''
    yield from bps.mv(det.cam.acquire_time, acq_time) 
    print(det.cam.acquire_time.read()) 
    yield from bps.mv(fs, 1) 
    dark_uid = yield from bp.count([det], md={'name':'dark'}) 
    yield from bps.mv(fs, 0) 
    light_uids = [] 
    
    for _ in range(reps): 
        light_uid = yield from bp.count([det], md={'name':'primary'}) 
        light_uids.append(light_uid) 
    
    return (dark_uid, light_uids) 

@inject_md_decorator({'macro_name': 'level_s_stage'})    
def level_s_stage():
    """level_s_stage level s_stage vx, vy

    double wafer stage: (-85, 85), (-58, 85)
    """
    # level on y axis
    yield from bps.mv(s_stage.px, 20, s_stage.py, -46)
    yield from level_stage_single(lrf, s_stage.vy, s_stage.py, 105, -46)

    # level on x axis
    yield from bps.mv(s_stage.px, 28,29, s_stage.py, 0)
    yield from level_stage_single(lrf, s_stage.vx, s_stage.px, -73,28 )

    # level on y axis
    yield from bps.mv(s_stage.px, 20, s_stage.py, -46)
    yield from level_stage_single(lrf, s_stage.vy, s_stage.py, 105, -46)


@inject_md_decorator({'macro_name': 'tablev_scan'})
def tablev_scan():
    '''
    send signal to DO01 to trigger tablev_scan
    '''
    yield from bps.mv(table_trigger, 0) # start tablev_scan
    yield from bps.sleep(1)
    
    # sleep until we see the busy signal go high
    cnt = 0
    while (table_busy.read()[table_busy.name]['value'] < 0.5) and cnt < 100: 
        print('waiting for busy signal...') 
        yield from bps.sleep(2)
        cnt += 1 

    # Turn off trigger signal
    yield from bps.mv(table_trigger, 1)

@inject_md_decorator({'macro_name':'rand_exp_test'})
def rand_exp_test(det, num, tcounts, img_key = 'pilatus1M_image'):
    '''
    take a series of random exposures within the wafer area
    set the exposure time based on the maximum signal that you see
    
    :param num: number of exposures to take
    :type num: int
    '''
    
    # set the current exposure time
    #det.cam.acquire_time.set(10)
    curr = det.cam.acquire_time.get()

    # get the current location
    wx = px.user_readback.get()
    wy = py.user_readback.get()

    # generate num many random positions within the wafer
    xPos = np.random.randint(wx-20,high=wx+20,size=num)
    yPos = np.random.randint(wy-20,high=wy+20,size=num)

    xPos = np.sort(xPos)
    yPos = np.sort(yPos)

    # scan through each coordinate and take an image
    yield from bp.list_scan([det],px,xPos,py,yPos)

    # grab the data
    results = db[-1].table(fill=True)['pilatus1M_image']

    # set based on the maximum signal that you find
    top = 0
    for img in results:
        arr = img[0]
        print('Max Pixel Value ' + str(np.max(arr)))
        if np.max(arr) > top:
            top = np.max(arr)

    # calculate the new exposure time
    new = (curr*tcounts/top)

    # set the new exposure time
    det.cam.acquire_time.set(new)

    print(f'New exposure time of {new} seconds')

@inject_md_decorator({'macro_name':'yale_fourin'})
def yale_fourin(det,locs,md='None'):
    print('Plan start')
    yield from bp.list_scan([det],px,locs[0],py,locs[1],md=md)
    print('Plan finish')




@inject_md_decorator({'macro_name':'opt_two_wafer'})
def opt_two_wafer(wafer1md={'wafer':'wafer1'},wafer2md={'wafer':'wafer2'},opt=False, laser=False, skip=0, wskip=False):
    """
    this plan uses a series of helper functions, adaptive optimization plans, and hitp plans to automatically align two 3in wafers, determine measurement locations, set exposure time, and collect data
    :param wafer1: metadata associated with the wafer1 position
    :type wafer1: dict
    :param wafer2: metadata associated with the wafer2 position
    :type wafer2: dict
    :param opt: choice to set the exposure time adaptively 
    :type opt: either None or a float with target counts
    :param laser: choice to use the laser range finder as a detector (for debugging)
    :type laser: bool
    :param skip: number of points to skip per wafer -- if wskip=1 then skip will be applied to the second wafer; otherwise it will only skip points on the first wafer
    :type skip: int
    :param wskip: whether to skip the first wafer or not
    :type wskip: bool
    """

    # all of this is defined for the pilatus1M detector,the xpress3 vortex, the laser range finder, and two motors (x and y)   

    # you can't turn on opt and use the laser range finder as a detector
    if (opt) and (laser):
        print("You can\'t optimize acquisition time on the laser range finder.")
        return
    
    # first let's bring everything home
    yield from home()

    # for debugging purposes, delete later
    if laser == True:
        det = lrf
    else:
        det = pilDet

    # outline of the plan
    #   - move to the first wafer
    #   - do an x-y alignment using the xpress3 (assume that rois are set correctly and monitor total counts)
    #   - derive sample locations based on the alignment
    #   - set exposure time using random sampling of 10 locations
    #   - perform loc_177 scan on the wafer
    #   - move to the next wafer and repeat

    # check whether to skip the first wafer or not
    if wskip == False:

        ### ~.~.~.~.~ WAFER ONE (1) ~.~.~.~.~ ###
        # first move to the rough location of wafer1
        # this will break if wafer1, wafer2, and home are not set correctly
        yield from wafer1()

        # now perform the alignment 
        # you need to collect and reset the motor offsets before and after every scan
        curr_offsets = [px.user_offset.get(),py.user_offset.get()]

        # do the alignment
        # this command will change the motor offsets
        yield from align_wafer(xsp3,px,py,md=wafer1md)
    
        # if chosen, set the exposure time using rand_exposure_test
        if opt:
            # get the current exposure time and save for later
            curr_exp = det.cam.acquire_time.get()
            # if opt is chosen then opt = # of desired counts
            # take 10 test exposures for now
            num = 10
            yield from rand_exp_test(det, num, opt, img_key = 'pilatus1M_image')

        # now we can collect the data
        # use Suchi's loc_177 locations and scan

        yield from loc_177_scan([det], skip=skip, md=wafer1md)



        # reset the motor offsets
        px.user_offset.set(curr_offsets[0])
        py.user_offset.set(curr_offsets[1])


    # now do the same thing for wafer #2
    ### ~.~.~.~.~ WAFER TWO (2) ~.~.~.~.~ ###
    yield from wafer2()

    # do the alignment
    # grab the offsets first
    curr_offsets = [px.user_offset.get(),py.user_offset.get()]
    yield from align_wafer(xsp3,px,py,md=wafer2md)

    # if chosen, set the exposure time using rand_exposure_test
    if opt:
        # get the current exposure time and save for later
        curr_exp = det.cam.acquire_time.get()
        # opt = # of desired counts
        num = 10
        yield from rand_exp_test(det,num,opt,img_key = 'pilatus1M_image')

    # now collect the data
    if wskip == False:
        yield from loc_177_scan([det],skip=0,md=wafer2md)
    else:
        yield from loc_177_scan([det],skip=skip,md=wafer2md)




    # reset the motor offsets
    px.user_offset.set(curr_offsets[0])
    py.user_offset.set(curr_offsets[1])

    # reset the acquisition time if necessary
    if opt:
        det.cam.acquire_time.set(curr_exp)


    # bring everything back home
    yield from home()

@inject_md_decorator({'macro_name':'two_wafer'})
def two_wafer(det, wafer1md={'purpose':'testing'},wafer2md={'purpose':'testing'}):
    # don't try so hard

    # get the current offsets
    curr_offsets = [px.user_offset.get(),py.user_offset.get()]

    #move to the first wafer
    yield from wafer1()

    # align
    yield from align_wafer(xsp3,px,py,md=wafer1md)

    # do the 177 loc scan
    yield from bp.list_scan([det],px,-loc177[0],py,loc177[1],md=wafer1md)

    #reset the motors
    px.user_offset.set(curr_offsets[0])
    py.user_offset.set(curr_offsets[1])

    # move to wafer2
    yield from wafer2()

    # align the sample
    yield from align_wafer(xsp3,px,py,md=wafer2md)

    # do the 177 loc scan
    yield from bp.list_scan([det],px,-loc177[0],py,loc177[1],md=wafer2md)

    # reset the motors
    px.user_offset.set(curr_offsets[0])
    py.user_offset.set(curr_offsets[1])

    # move back home
    yield from home()
