=======
Devices
=======

A variety of devices are available for use at SSRL-1-5.  Currently only 
High Throughput (HiTp) diffraction is supported, but more functionality will
be added in the future.  

While most PV's are accessible from the ipython session, it's generally 
advised to use the GUI elements to adjust parameters like exposure time or 
frame rates.  


Area detectors
==============

Dexela Area Detector: ``dexDet``
--------------------------------
The Dexela area detector requires dark field correction.  We have already 
included a plan for this purpose. 

.. code:: ipython 

    In [1]: RE( bp.count([dexDet]) ) # basic count plan

    In [2]: uids = RE(dark_light_plan([dexDet], shutter)) # take a dark image followed by a light image


More to come later?
-------------------

Fluorescence detectors
======================

Xspress3 Fluorescence Detector: ``xsp3``
----------------------------------------
The Xspress3 detector writes .h5 files on each acquisition.  Both the full 
multi-channel arrays (MCA's) and integrated ROI values are accessible via PV 
access, and can be inspected directly on the python interpreter.  Normally
ROI ranges should be adjusted from the EDM display. 

.. code:: ipython

    #TO-DO inspect ROI values?

Taking single measurements via ``bp.count`` is valid.

.. code:: ipython

    In [1]: RE(bp.count([xsp3]))

If taking multiple acquisitions in one run, we must make sure the ``xsp3.total_points``
variable matches the number of acquisitions to be taken.  This ensures that all MCA's 
in one run will be placed in a single h5 file.  Bluesky and Databroker assume 
this behavior when accessing saved data.  *We have done our best to create plans 
that cover this use case*, but if needed this value can be adjusted manually.

.. code:: ipython

    In [1]: RE(bps.mv(xsp3.total_points, 5))

    In [2]: RE(bp.scan([xsp3], motor, -1, 1, 5))

    In [3]: db[-1].table(fill=True)
    Out [3]: # TO-DO output for table.


Motors
======

Sample Stage: ``s_stage``
-------------------------

``s_stage`` has the following components, used to control the sample setup

=================================== ======================= ==================
Component name                      Motor name              Units
=================================== ======================= ==================
``px``                              Plate x                 mm
``py``                              Plate y                 mm
``pz``                              Plate z                 mm
``vx``                              Vert x                  steps
``vy``                              Vert x                  steps
=================================== ======================= ==================

.. code:: ipython

    In [1]: RE( bps.mv(s_stage.px, 0) ) # move stage plate x to 0

    In [1]: RE( bps.mvr(s_stage.pz, -1) ) # move stage height -1 from current position
