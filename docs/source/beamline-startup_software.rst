===================================
Beamline Startup: EPICS and Bluesky
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
folder and run the ``st.cmd`` script file.  IOC's should be started with sudo 
access, via the ``specadm`` account.  

IMS motors (stage px, py, pz)
-----------------------------
.. code:: console

    [specadm@blueepicslx ~]$ cd /opt/EPICS/3.14/iocs/motor/iocBoot/ioc-ims/
    [specadm@blueepicslx ~]$ ./st.cmd

PICO motors (stage vx, vy)
--------------------------
.. code:: console

    [specadm@blueepicslx ~]$ cd /opt/EPICS/3.14/iocs/motor/iocBoot/ioc-picoPMNC87xx/
    [specadm@blueepicslx ~]$ ./st.cmd

Galil RIO (laser range finder, I0, I1, shutter)
-----------------------------------------------
.. code:: console

    [specadm@blueepicslx ~]$ cd /opt/EPICS/3.14/iocs/galil_rio/iocBoot/ioc-galil-rio/
    [specadm@blueepicslx ~]$ ./st.cmd

XSPRESS3 (multi channel fluorescence detector)
----------------------------------------------
Sometimes EPICS is misconfigured.  Check to make sure the environment variable 
`EPICS_CAS_INTF_ADDR_LIST` is not set.  You can unset this once ssh'd into the 
XSPRESS3 computer.  It appears that this variable is reset when the xspress3 
computer is restarted

This IOC is best started on the xspress3 computer directly:

.. code:: console 

    [xspress3@xspress3 ~]$ env | grep CA
    EPICS_CAS_INTF_ADDR_LIST=localhost
    EPICS_CA_AUTO_ADDR_LIST=NO
    EPICS_CA_ADDR_LIST=localhost
    [xspress3@xspress3 ~]$ unset EPICS_CAS_INTF_ADDR_LIST

Starting the ioc can be done either from bluedev via the alias `xspress3-2-ioc`:

.. code:: console
    
    (collect) [b_spec@bluedevlx ~]$ xspress3-2-ioc

Or from the xspress3 box directly: 

.. code:: console

    [xspress3@xspress3 ~]$ /usr/bin/xspress3-ioc.sh

Area Detector (MarCCD)
----------------------
The IOC for the mar detector must be on and have access to the data directory 
(/home/data).  At the moment this necessitates starting from BlueDevLX.  

.. code:: console

    (collect) [b_spec@bluedevlx ~]$ cd iocs/marCCD/iocBoot/ioc-marCCD/
    (collect) [b_spec@bluedevlx ioc-marCCD]$ ./st.cmd




Profile Configuration:
======================

Detector Change
---------------
From Bluesky's point of view, a device is initialized when its constructor is 
called.  This is done when the device configuration file is imported.  Thus, to 
activate a device, simply add it to the import list in 
``<ipython_profile_dir>/instrument/devices/__init__.py``.  
This is true for any device, not just detectors.  

.. code:: python
        
    from .stages import *
    from .xspress3 import *
    from .dexela import *
    # from .marCCD import *
    # from .pilatus import *
    from .misc_devices import *


Bluesky: 
========
Bluesky runs in an interactive ipython console, which can be started with the 
alias ``bluesky`` on bluedevlx.slac.stanford.edu:

.. code:: console

    (collect) [b_spec@bluedevlx ~]$ bluesky

This will run a series of startup scripts which, among other things, start the 
RunEngine and connect to the database.  If any modifications need to be made to 
these files, they are located in ``~/ipystartup``

Importantly, if any of the above IOC's are not started, Bluesky will fail to 
start.  Bluesky attempts to connect to each device, and if one is not available 
the startup process fails.  Error messages should reveal which IOC's are not 
running, if problems arise.  

Before editing these files, please contact Robert Tang-Kong (roberttk at slac). 

User Information
----------------
When a new user gets started at the beamline, the RunEngine needs to record that 
user's information.  The metadata associated with all runs is stored in the 
RunEngine itself, and can be changed with the following syntax:  

.. code:: python

    RE.md['key'] = 'item'

This metadata is carried over between Bluesky Ipython sessions, so be wary of 
not updating this information.  The convenience function ``show_md()`` has been
provided to allow easy viewing of this information, though ``RE.md`` can be 
manipulated as a simple Python dictionary would.
