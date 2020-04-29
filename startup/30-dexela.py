from ophyd import EpicsSignal, Component as Cpt
from ssrltools.devices.dexela import SSRLDexelaDet, DexelaTiffPlugin

print('-------------------30-dexela.py startup file')

class DexelaDet15(SSRLDexelaDet):
    """
    Final class for Dexela Detector on SSRL BL 1-5
    - add Plugins (TIFF plugin, etc)

    det = DexelaDet15(prefix, name='name')
    """
    # DexelaDetector from ophyd pulls in all Dexela specific PV's
    write_path = 'path/here/to/thing'
    # In case where TIFF plugin is being used
    tiff = Cpt(DexelaTiffPlugin, 'TIFF1:',
                        write_path_template=write_path,
                        read_path_template=write_path)
    # Else there should be an NDArrayData PV
    image = Cpt(EpicsSignal, 'ArrayData')

    def trigger(self):
        super().trigger()
        
    # Could add more attributes to file_plugin
    # could add stage behavior


# Connect PV's to Ophyd objects

dexDet = DexelaDet15('PVName:', name='dexela')