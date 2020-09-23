===================================
Beamline Startup, EPICS and Bluesky
===================================

Currently the beamline devices are all controlled via EPICS_, and the data 
collection orchestrated via the Bluesky_ Ecosystem.  Each of these systems must 
be started to render the beamline operational.  

.. _EPICS: https://epics.anl.gov/
.. _Bluesky: https://blueskyproject.io/

.. Note:: This system is still under development at SSRL.  Many tasks may seem 
    tedious, but there is significant room for streamlining the process.  Please
    view this list of startup items in that lens, and be patient.  

To start up EPICS, the IOCs (Input-Output Controllers) must be started.  Each 
set of devices has its own IOC

EPICS:
======
These IOCs will eventually be bundled into a single command, but for now each 
must be started individually.  IOC's are currently housed on 
blueepicslx.slac.stanford.edu.  The patten is the same, navigate to the correct
folder and run the ``st.cmd`` script file

IMS motors (stage px, py, pz)
-----------------------------
.. code:: console

    (collect_2020q2) [b_campen@blueepicslx ~]$ cd /opt/EPICS/3.14/iocs/motor/iocBoot/ioc-ims/
    (collect_2020q2) [b_campen@blueepicslx ~]$ ./st.cmd

PICO motors (stage vx, vy)
--------------------------
.. code:: console

    (collect_2020q2) [b_campen@blueepicslx ~]$ cd /opt/EPICS/3.14/iocs/motor/iocBoot/ioc-picoPMNC87xx/
    (collect_2020q2) [b_campen@blueepicslx ~]$ ./st.cmd

Galil RIO (laser range finder, I0, I1, shutter)
-----------------------------------------------
.. code:: console

    (collect_2020q2) [b_campen@blueepicslx ~]$ cd /opt/EPICS/3.14/iocs/galil_rio/iocBoot/ioc-galil-rio/
    (collect_2020q2) [b_campen@blueepicslx ~]$ ./st.cmd


Bluesky: 
========
Bluesky runs in an interactive ipython console, which can be started with the 
alias ``bluesky`` on bluedevlx.slac.stanford.edu:

.. code:: console

    (collect) [b_spec@bluedevlx ~]$ bluesky

This will run a series of startup scripts which, among other things, start the 
RunEngine and connect to the database.  If any modifications need to be made to 
these files, they are located in ``~/ipystartup``

Before editing these files, please contact Robert Tang-Kong (roberttk at slac). 
