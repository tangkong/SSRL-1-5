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
# Try databroker v2 maybe, at some point
    fig, axes = plt.subplots(1,2, sharey=True, figsize=(7, 4.9),
                            gridspec_kw={'width_ratios': [3,1]})
    
    arr = db[ind].table(fill=True)[img_key][data_pt][0]
    vmax = np.mean(arr)+3*np.std(arr)
    n_max = np.sum(arr>nax_val)
    
    axes[0].imshow(arr, vmax=vmax)
    axes[0].text(100,100, f'{n_max} pixels > {max_val}', 
                    backgroundcolor='w')
    
    sl = arr[:, 900:1100]
    axes[1].plot(sl.sum(axis=1), list(range(2048)))
    plt.tight_layout()