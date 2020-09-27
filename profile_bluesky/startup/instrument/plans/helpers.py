"""
Helper plans, functions

"""
from ..framework.initialize import db

import numpy as np

__all__ = ['show_table', 'show_image', ]

def show_table(ind=-1):
    return db[ind].table()

def show_image(ind=-1, data_pt=1, img_key='marCCD_image'): 
    # Try databroker v2 maybe, at some point
    arr = db[ind].table(fill=True)[img_key][data_pt][0]
    vmax = np.mean(arr)+3*np.std(arr)

    plt.imshow(arr, vmax=vmax)
    plt.colorbar()