"""
Helper plans, functions

"""
from ..framework.initialize import db
from ..devices.stages import px,py,pz
from ..devices.misc_devices import filter1, filter2, filter3, filter4
from ..devices.xspress3 import xsp3

import bluesky.plans as bp
import bluesky.plan_stubs as bps

import matplotlib.pyplot as plt
import numpy as np
import time
#import pyFAI
#import fabio
#from pyFAI.test.utiltest import UtilsTest
#from pyFAI.calibrant import CALIBRANT_FACTORY
#from pyFAI.goniometer import SingleGeometry


__all__ = ['reset_offset','show_table', 'show_image', 'show_scan', 'avg_images', 'filters',
           'center','home','copper','calib','wafer1','wafer2','wmx','wmy', 
           'w1', 'w2']

def show_table(ind=-1):
    return db[ind].table()

def show_image(ind=-1, data_pt=1, img_key='pilatus1M_image', max_val=500000):
    """show_image attempts to plot area detector data, plot a vertical slice, 
    and calculates number of pixels above the provided threshold.  

    :param ind: Index of run, -1 referring to most recent run. defaults to -1
    :type ind: int, optional
    :param data_pt: row of run to plot, defaults to 1
    :type data_pt: int, optional
    :param img_key: column name holding image data, defaults to 'marCCD_image'
    :type img_key: str, optional
    :param max_val: max pixel threshold, defaults to 60000
    :type max_val: int, optional
    """
    # Try databroker v2 maybe, at some point
    if img_key in ['pilatus300k_image']:
        horizontal=True
    else:
        horizontal=False

    try:
        hdr = db[ind].table(fill=True)
        arr = hdr[img_key][data_pt][0]
        if horizontal:
            arr = np.rot90(arr, -1)
    except KeyError:
        print(f'{img_key} not found in run: {ind}, data point: {data_pt}')
        return

    fig, axes = plt.subplots(1,2, sharey=True, figsize=(7, 4.9),
                            gridspec_kw={'width_ratios': [3,1]})
    
    vmax = np.mean(arr)+3*np.std(arr)
    n_max = np.sum(arr>max_val)
    
    axes[0].imshow(arr, vmax=vmax)
    axes[0].text(100,100, f'{n_max} pixels > {max_val}', 
                    backgroundcolor='w')
    
    scan_no = db[ind].start['scan_id']
    axes[0].set_title(f'{img_key}, Scan #{scan_no}, data point: {data_pt}')

    height, width = arr.shape
        
    sl = arr[:, int(0.45*width):int(0.55*width)]
    axes[1].plot(sl.sum(axis=1), list(range(height)))
    plt.tight_layout()

def show_scan(ind=-1, dep_subkey='channel1_rois_', indep_subkey='s_stage'):
    """show_scan attempts to plot tabular data.  Looks for dependent and 
    independent variables based on provided subkeys

    :param ind: Index of run, -1 referring to most recent run., defaults to -1
    :type ind: int, optional
    :param dep_subkey: dependent variable search term, defaults to 'channel1_rois_roi01'
    :type dep_subkey: str, optional
    :param indep_subkey: independent variable search term, defaults to 's_stage'
    :type indep_subkey: str, optional
    """
    df = db[ind].table()
    scan_no = db[ind].start['scan_id']

    # grab relevant keys
    dep_keylist = df.columns[[dep_subkey in x for x in df.columns]]
    dep_key = dep_keylist[0]
    indep_keylist = df.columns[[indep_subkey in x for x in df.columns]]
    indep_key = indep_keylist[0]
    
    try:
        fig, ax = plt.subplots()
        ax.set_title(f'Scan #{scan_no}')
        
        for key in indep_keylist:
            df.plot(indep_key, dep_key, marker='o', figsize=(8,5))

    except KeyError:
        print(e)
        return


def avg_images(ind=-1,img_key='marCCD_image'):
    """avg_images [summary]

    [extended_summary]

    :param ind: Run index, defaults to -1.  
                If negative integer, counts backward from most recent run (-1=most recent, -2=second most recent)
                If positive integer, matches 'scan_id'
                If string, interprets as the start of a UID (ex: '8ee443d')
    :type ind: int, optional
    :param img_key: [description], defaults to 'marCCD_image'
    :type img_key: str, optional
    :return: [description]
    :rtype: [type]
    """
    ''' Tries to average images inside a run.  
    Currently assumes MarCCD format 
    returns the array after.'''

    df = db[ind].table(fill=True)

    #gather images
    arr = []
    for i in range(len(df)):
        arr.append(df[img_key][i+1][0])

    avg_arr = np.sum(arr, axis=0) / len(arr)

    # plot
    fig, axes = plt.subplots(1,2, sharey=True, figsize=(7, 4.9),
                            gridspec_kw={'width_ratios': [3,1]})
    
    vmax = np.mean(avg_arr)+3*np.std(avg_arr)

    axes[0].imshow(avg_arr, vmax=vmax)
    
    scan_no = db[ind].start['scan_id']
    axes[0].set_title(f'Scan #{scan_no}, averaged over {len(arr)} images')

    sl = avg_arr[:, 900:1100]
    axes[1].plot(sl.sum(axis=1), list(range(2048)))
    plt.tight_layout()

    return avg_arr

def show_config(ind=-1):
    config = db[ind].descriptors[0]['configuration']
    config_dict = {}
    for k in config.keys():
        config_dict.update({k: config[k]['data']})

    return config_dict


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

#calibration = [0.2466,0.008,0.5419,0.79989,0.066833,0.085106,1,0.142]

def recalib(img):
    # messing around with pyFAI's recalibration code
    # starting from the tutorial jupyter notebook given in the pyFAI documentation
    # http://www.silx.org/doc/pyFAI/dev/usage/tutorial/Recalib/Recalib_notebook.html
    
    # the example opens an edf image file with fabio
    # i will try with an NxM sized numpy array of pixel values

    # get approximate positions
    x = img.shape[0]/2 # x beam center in pixels
    y = img.shape[1]/2 # y beam center in pixels
    d = 246.6 # sample-detector distance in mm
    wl = 0.7999 # wavelength 

    # define a detector and calibrant
    #pilatus = pyFAI.detector_factor('Pilatus1M')
    #calib = CALIBRANT_FACTORY("Lab6")

