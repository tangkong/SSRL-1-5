from collections import OrderedDict
from ssrltools.devices.xspress3 import SSRLXspress3Detector
from ophyd import Signal

print('-------------------20-xspress3.py startup file')

xsp3 = SSRLXspress3Detector('XSPRESS3-EXAMPLE:', name='xsp3', roi_sums=True)

# bp=blueskyplans, imported by nslsii startup configuration, 
xsp3.settings.configuration_attrs = ['acquire_period',
			           'acquire_time',
			           'gain',
			           'image_mode',
			           'manufacturer',
			           'model',
			           'num_exposures',
			           'num_images',
			           'temperature',
			           'temperature_actual',
			           'trigger_mode',
			           'config_path',
			           'config_save_path',
			           'invert_f0',
			           'invert_veto',
			           'xsp_name',
			           'num_channels',
			           'num_frames_config',
			           'run_flags',
                        'trigger_signal']

for n, d in xsp3.channels.items():
    roi_names = ['roi{:02}'.format(j) for j in [1, 2, 3, 4]]
    d.rois.read_attrs = roi_names
    d.rois.configuration_attrs = roi_names
    for roi_n in roi_names:
        getattr(d.rois, roi_n).value_sum.kind = 'omitted'
