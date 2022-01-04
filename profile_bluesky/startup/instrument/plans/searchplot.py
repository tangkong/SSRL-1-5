from ..framework.initialize import db
import numpy as np
import matplotlib.pyplot as plt
import pyFAI 
from scipy import signal
### functions for searching through a databroker with a specific structure, finding data, and creating pre-specified plots

__all__ = ['data_reduction','waferplot',]

### this is entirely hardcoded to the high-throughput setup at beamline 1-5, stanfrod synchrotron radiation laboratory

calibration = [0.2466,0.008,0.5419,0.79989,0.066833,0.085106,1,0.142]
def data_reduction(imArray,QRange=None, ChiRange=None):
    s1 = int(imArray.shape[0])
    s2 = int(imArray.shape[1])
    imArray = signal.medfilt(imArray, kernel_size=5)
    detector_mask = np.ones((s1, s2)) * (imArray <= 0)
    lamda = 0.7999
    PP = 1
    #p = pyFAI.AzimuthalIntegrator(wavelength=lamda)
    #p.setFit2D(d, x0, y0, tilt, Rot, pixelsize, pixelsize)
    p = pyFAI.AzimuthalIntegrator(wavelength=lamda, detector=pyFAI.detector_factory('pilatus1M'), 
            dist=0.2466, poni1=0.06683, poni2=0.0851, rot1=0.008086, rot2=0.5419, rot3=2.763068)
    cake, Q, chi = p.integrate2d(imArray, 1000, 1000,mask=detector_mask, polarization_factor=PP)
    Q = Q * 10e8
    centerChi = (np.max(chi) + np.min(chi)) / 2
    if (QRange is not None) and (ChiRange is not None):
        azRange = (centerChi + ChiRange[0], centerChi + ChiRange[1])
        radRange = tuple([y / 10E8 for y in QRange])
        print(azRange, radRange)
    else:
        azRange, radRange = None, None

    Qlist, IntAve = p.integrate1d(imArray, 1000,azimuth_range=azRange, radial_range=radRange,mask=detector_mask, polarization_factor=PP)
    Qlist = Qlist * 10e8
    chi = chi - centerChi
    return Q, chi, cake, Qlist, IntAve

def waferplot(name=None, n=0,take=-1,img_key='pilatus1M_image',show_stage_calib=None):
    # search for a specific data point on a combinatorial wafer library and create plots

    # this function works for runs with the md tag 'wafer':'name'
    # where name is specified by the user
    # if the wafer has n scans then waferplot will return a plot for the nth point
    # if plot is specified it will plot the raw image
    # if qchi is specified it will try to integrate the image

    # if calibration == True then it will plot the fits of any calibration done to the stage beforehand, such as scanning in x and y with the xpress3 to find wfafer boundaries. this can be used in the case that a user is unsure if the sample was aligned correctly, or to check if an error was made in an automatic fitting routine

    query = list(db(wafer=str(name)))[take]


    # we are assuming a pilatus 1m detector if none other is provided
    try: 
        img = results.table(fill=True)[img_key][n+1][0]
    except: 
        print(f'no results found for {name}, try a different value for "name"')
        return

    fig,ax = plt.subplots(1,3,figsize=(15,5))
        
    # for an a X b sized image assume img.shape = (1, a, b)
    mn = np.mean(img.flatten())
    std = np.std(img.flatten())
    ax[0].imshow(img,vmax=mn+3*std)
    ax[0].set_title(str(name))

    res = data_reduction(img)
    
    ax[1].pcolormesh(res[0],res[1],res[2],vmax=mn+3*std)
    ax[1].set_xlabel('q (' + r'$\AA^{-1}$)')
    ax[1].set_ylabel(r'$\chi$')
    ax[1].set_ylim(0, 180)
    ax[1].set_title(f'Position {n}')

    ax[2].plot(res[3],res[4],'k-')
    ax[2].set_xlabel('q (' + r'$\AA^{-1}$)')
    ax[2].set_ylabel('Intensity (photons)')


