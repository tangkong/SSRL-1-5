================
Sample Alignment
================


The Theory
==========
Sample alignment can be a challenging process, particularly if the sample 
"gets lost" at any point.  It is important to remember that there is a method 
to the madness, and you can always start from the beginning to be sure of 
where the sample lies.  With a better understanding of the sample geometry it 
is of course possible to skip steps and align faster.  However, cutting corners 
can also get you lost, so when in doubt take your time.  

In this experiment, for a sample to be aligned we are looking to perform the 
following steps: 

#. Stage leveling
#. Theta calibration
#. Stage height calibration
#. x-y calibration
#. xspress3 calibration
#. Sample alignment 

[image of stage, top down, axes labeled]

[image of stage in 3d, beam path context]


Stage leveling
--------------
Stage leveling is performed by adjusting the pico motors and reading the stage 
height with the laser range finder.  The ``level_s_stage`` plan attempts to do 
both the x and y axes, but to level only one ``level_stage_single`` can be used.  

.. code-block:: ipython

    In [1]: %mov py 0

    In [2]: # detector, pico, stage motor, pos over pico, pos to reference
    RE(level_stage_single(lrf, vx, px, -50, 50))

    In [3]: %mov px 43

    In [4]: RE(level_stage_single(lrf, vy, py, 75, -75))


Theta Calibration
-----------------
With the stage leveled, we set the theta motor offset such that theta reads 0. 
Rough calibration is usually done with a simple bubble level and later refined 
using the beam.  This is done by iterating through:

- Scan beam stop w.r.t. theta
- Move to theta where signal is maximized
- Scan beam stop w.r.t. stage height (pz)
- Move to theta where **derivative** is maximized


Stage height calibration
------------------------
This should be done in coordination with theta calibration.  


Stage x-y Alignment
-------------------
Centering the beam on the stage is obviously important, and can be accomplished 
in a variety of ways.  The simplest is often to move theta to some angle 
(1-2 degrees), find the center of a sample (copper dot), then center the laser 
on the dot.  The stage can then be moved such that the laser is in the center of 
the stage, and px/py zeroed.  Alternately one can use phosphor tape to find the 
beam.  

It is important to remember the offsets found during this alignment, as we will 
want to return to this as a 'home' setting.


Xspress3 MCA calibration
------------------------
If this has not yet been done, move to a piece of copper foil and calibrate the 
Xspress3.  
See :ref:`xsp3-calibration` section for detailed instructions.  




