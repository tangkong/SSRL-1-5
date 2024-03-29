Data Collection
===============

Here we will go through the typical steps needed to collect data on a 
combinatorial library with the high throughput (HiTp) XRD setup.  There are 
many different types of samples that can be run, and we have tried to provide 
plans that cover the most common use cases. 

Here we will cover what typically happens once a sample has been loaded and 
the stage aligned.  This includes:

- basic use of plans
- Standard adding of metadata
- scripting higher level macros


Basic plan choice
-----------------
There are a variety of plans available at your disposal to take data on wafer 
libraries.  They are described in detail in :ref:`hitp-plans`.  Some suggestions:

**Take a single exposure.** If you want to measure a single spot for 
diagnostic purposes, or for a single sample.  Note: exposure time is set per 
detector, as you can count from multiple detectors in a single call.

.. code-block:: ipython
    
    In [1]: RE(bp.count([pilDet]), purpose='testing')

**Scan a detector with a motor.** See :ref:`scanning-detectors <scanning-detectors>`

The Xspress3 needs to know how many points are being measured before acquisition, 
so the command is a bit longer

.. code-block:: ipython

    In [1]: num=50; xsp3.total_points.put(num); RE(bp.rel_scan([xsp3], py,-45,45, 
       ...: num=num, md={'purpose':'align'}))


**Run a "wafer-library".** Combinatorial samples are often deposited on a 
silicon wafer, requiring a slightly modified grid scan.  

The classic 177 point case.  Has the option to specify some number of points 
to skip, if a run was interrupted.  

.. code-block:: ipython
    
    In [1]: RE(loc_177_scan([pilDet], skip=0), sample_id='XX001', 
                purpose='measurement')

You can also supply your own locations.  The same skip functionality exists. 
A few location lists are provided, but you can always generate your own.  

.. code-block:: ipython
    
    In [1]: RE(loc_cust_scan([pilDet], locYale41, skip=10), 
             sample_id='XX001', purpose='measurement')

If you would like to confirm the order of acquisition, you can pass the laser 
range finder in as the detector and watch the acquisition

.. code-block:: ipython
    
    In [1]: RE(loc_cust_scan([lrf], locYale41, skip=10), purpose='testing')


Managing metadata
-----------------
Labeling your runs is of critical importance.  The syntax of this has been 
covered in :ref:`managing-metadata`, but some guiding principles will be 
provided here.  

Metadata is stored in "key-value pairs".  If you execute: 

.. code-block:: ipython

    In [1]: RE(plan(), sample_id='A', purpose='calibration')


``sample_id`` and ``purpose`` are keys, while ``A`` and ``caibration`` are 
their respective values.  

Your metadata keys should be consistent across your dataset, otherwise you will 
have difficulty finding your data.  For example, if you end up using both 
``sample_name`` and ``name`` to label your runs, you may end up missing data 
when you search the databroker later. 

As a fall back option, you can remember the scan number of any run that you 
believe will be important.  The scan number is automatically incremented for 
each plan/scan that is run, and is an easy way to record runs.  Writing these 
down in your own notes is recommended.  

Useful keys to add: 

- ``sample_name`` : 'A', 'B', 'test_wafer' ... 
- ``purpose``: 'calibration', 'data', 'testing' ...


Keys that are recorded automatically (as in you don't need to add them yourself): 

- ``time`` - In this context, the start time. (Other times are also recorded.)
- ``uid`` - a globally unique ID for this run
- ``plan_name`` - the function or class name of plan (e.g., 'count')
- ``plan_type`` - e.g., the Python type of plan (e.g., 'generator')


Extending to the two wafer setup
--------------------------------
Collecting data on two wafers is a simple extension of the plans we have 
discussed earlier.  This plan is a bit verbose for the sake of demonstration. 

.. code-block:: python

    @inject_md_decorator({'macro_name':'two_wafer'})
    def two_wafer(wafer1md={'purpose':'testing'},wafer2md={'purpose':'testing'}):
        # get the current offsets
        curr_offsets = [px.user_offset.get(),py.user_offset.get()]

        #move to the first wafer, assuming we know the center
        yield from bps.mv(px, w1_centerx, py, w1_centery)

        # do the 177 loc scan
        yield from bp.list_scan([det],px,-loc177[0],py,loc177[1],md=wafer1md)

        #reset the motors
        yield from bp.mv(px.user_offset, curr_offsets[0], 
                         py.user_offset, curr_offsets[1])

        #move to the second wafer, assuming we know the center
        yield from bps.mv(px, w2_centerx, py, w2_centery)

        # do the 177 loc scan
        yield from bp.list_scan([det],px,-loc177[0],py,loc177[1],md=wafer2md)

        #reset the motors
        yield from bp.mv(px.user_offset, curr_offsets[0], 
                         py.user_offset, curr_offsets[1])

