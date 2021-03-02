============================
Device Configuration Details
============================

This section is mostly for Beamline Support in setting up devices.  
Bluesky/EPICS relies on specific device configurations in some cases, so one may
refer here in the case of strange behavior.  

-------------------------------
Xspress3 Multi Channel Analyzer
-------------------------------
There are a plethora of options available in the Xspress 3 EPICS IOC.  The most 
relevant are listed below.  

+----------------------+--------------+
| PV name              | Setting      |
+----------------------+--------------+
| TriggerMode          | Internal (1) |
+----------------------+--------------+
| hdf5.file_write_mode | (2)          |
+----------------------+--------------+
| xsp3.                |              |
+----------------------+--------------+