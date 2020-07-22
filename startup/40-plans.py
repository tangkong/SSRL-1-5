print('-------------------40-plans.py startup file')

from ssrltools.plans import meshcirc, nscan, level_stage_single

# For scanning over all sample locations, try bp.list_scan or bp.list_grid_scan
# eg: bp.list_scan([dets], HiTpStage.sample_loc_list(), md={'sample': 'sample name', ...})


# collection plans
# Basic dark > light collection plan
import time 

def dark_light_plan(dets, fs, md={}):
    '''
        Simple acquisition plan:
        - Close shutter, take image, open shutter, take image, close shutter

        dets : detectors to read from
        motors : motors to take readings from (not fully implemented yet)
        fs : Fast shutter, high is closed
        sample_name : the sample name

        Example usage:
        >>> RE(dark_light_plan([dexDet], shutter, {sample_name='pt1'}))
    '''

    start_time = time.time()
    uids = []

    #yield from bps.sleep(1)

    #close fast shutter, take a dark
    yield from bps.mv(fs, 1)
    mdd = md.copy()
    mdd.update(name='dark')
    uid = yield from bp.count(dets, md=mdd)
    uids.append(uid)


    # open fast shutter, take light
    yield from bps.mv(fs, 0)
    mdl = md.copy()
    mdl.update(name='primary')
    uid = yield from bp.count(dets, md=mdl)
    uids.append(uid)

    return(uids)
    end_time = time.time()
    print(f'Duration: {end_time - start_time:.3f} sec')

# Plan for meshgrid + dark/light?...

# image time series
def expTimePlan(det, timeList=[1]):
    '''
    Run count with each exposure time in time list.  
    Specific to Dexela Detector, only run with single detector
    return uids from each count
    '''
    uids = []
    for time in timeList:
        # set acquire time
        yield from bps.mov(det.cam.acquire_time, time)
        uid = yield from bp.count([det], md=dict(acquire_time=time))

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
        if hdr.start['name']=='dark':
            darkarr = hdr.table(fill=True)['dexela_image'][1]
        elif hdr.start['name'] == 'primary':
            lightarr = hdr.table(fill=True)['dexela_image'][1]
        else:
            print('mislabeled data... ignoring for now')
            return

    bkgd_subbed = lightarr.astype(int) - darkarr.astype(int)
    bkgd_subbed[ bkgd_subbed < 0 ] = 0
    plt.imshow(bkgd_subbed, vmax = bkgd_subbed.mean() + 3*bkgd_subbed.std())

def plot_MCA(hdrs):
    '''Plot MCA's from given hdr
    '''
    plt.figure()
    data = hdr.table(fill=True)['xsp3_channel1'][1]

    plt.plot(data)
    plt.xlabel('Energy (keV)')
    plt.ylabel('Total counts')

def multi_run(acq_time, reps): 
    yield from bps.mv(dexDet.cam.acquire_time, acq_time) 
    print(dexDet.cam.acquire_time.read()) 
    yield from bps.mv(shutter, 1) 
    dark_uid = yield from bp.count([dexDet], md={'name':'dark'}) 
    yield from bps.mv(shutter, 0) 
    light_uids = [] 
    
    for i in range(reps): 
        light_uid = yield from bp.count([dexDet], md={'name':'primary'}) 
        light_uids.append(light_uid) 
    
    return (dark_uid, light_uids) 

def wa():
    ''' Is there a macro for this already?
    '''

    print(f'stage_x: {stage.stage_x.read()[stage.stage_x.name]["value"]}')
    print(f'stage_y: {stage.stage_y.read()[stage.stage_y.name]["value"]}')
    print(f'stage_z: {stage.stage_z.read()[stage.stage_z.name]["value"]}')
    print(f'theta: {stage.theta.read()[stage.theta.name]["value"]}')
           
