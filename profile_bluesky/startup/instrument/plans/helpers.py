"""
Helper plans, functions

"""
from ..framework.initialize import db

import matplotlib.pyplot as plt
import numpy as np

__all__ = ['show_table', 'show_image', ]

def show_table(ind=-1):
    return db[ind].table()

def show_image(ind=-1, data_pt=1, img_key='marCCD_image', max_val=60000):
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
    try:
        arr = db[ind].table(fill=True)[img_key][data_pt][0]
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

    sl = arr[:, 900:1100]
    axes[1].plot(sl.sum(axis=1), list(range(2048)))
    plt.tight_layout()

def show_scan(ind=-1, dep_subkey='channel1_rois_roi01', indep_subkey='s_stage'):
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

    # grab relevant keys
    dep_keylist = df.columns[[dep_subkey in x for x in df.columns]]
    dep_key = dep_keylist[0]
    indep_keylist = df.columns[[indep_subkey in x for x in df.columns]]
    indep_key = indep_keylist[0]

    try:
        df.plot(indep_key, dep_key, marker='o', figsize=(8,5))
    except KeyError:
        print(e)
        return