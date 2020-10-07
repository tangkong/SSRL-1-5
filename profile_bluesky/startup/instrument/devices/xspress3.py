"""
xspress3 configuration
"""

__all__ = ['xsp3', ]

from collections import OrderedDict, deque
import itertools
import time as ttime

from ophyd import Component as Cpt
from ophyd.sim import NullStatus  # TODO: remove after complete/collect are defined
from ophyd.areadetector.plugins import PluginBase
from ssrltools.devices.xspress3 import (Xspress3Channel, Xspress3FileStore, 
										XspressTrigger, Xspress3Detector)
from ophyd import Signal

from ..session_logs import logger

logger.info(__file__)

class SSRLXspress3Detector(XspressTrigger, Xspress3Detector):
    roi_data = Cpt(PluginBase, 'ROIDATA:')
    channel1 = Cpt(Xspress3Channel, 'C1_', channel_num=1, read_attrs=['rois'])
    channel2 = Cpt(Xspress3Channel, 'C2_', channel_num=2, read_attrs=['rois'])

    hdf5 = Cpt(Xspress3FileStore, 'HDF5:',
			   write_path_template='/home/xspress3/data',
               read_path_template='/home/xspress3/data'
               )

    def __init__(self, prefix, *, configuration_attrs=None, read_attrs=None,
                 **kwargs): 
        if configuration_attrs is None:
            configuration_attrs = ['external_trig', 'total_points',
                                   'spectra_per_point', 'settings',
                                   'rewindable']
        if read_attrs is None:
            read_attrs = ['channel1', 'channel2', 'hdf5']
        super().__init__(prefix, configuration_attrs=configuration_attrs,
                         read_attrs=read_attrs, **kwargs)

        self._asset_docs_cache = deque()
        self._datum_counter = None

    def trigger(self):
        if self.hdf5.capture.get() == 0:
            # create new resource document, stage does this the first time
            self.hdf5._fn = self.hdf5.file_template.get() % (self.hdf5._fp,
                                                        self.hdf5.file_name.get(),
                                                        self.hdf5.file_number.get())
            self.hdf5._generate_resource({})
            self.hdf5._filestore_res = self.hdf5._asset_docs_cache[-1][-1]
            
            #stage() turns this on once, but subsequent triggers don't
            self.hdf5.capture.put(1)
        ret = super().trigger()
        return ret
    def stop(self):
        # .stop() walks back to Device class... which does not return anything
        #print('>>>>>>>>>>>>>>>>>>>>>>>> xsp3.stop')
        ret = super().stop()
        self.hdf5.stop()
        return ret

    def stage(self):
        if self.spectra_per_point.get() != 1:
            raise NotImplementedError(
                "multi spectra per point not supported yet")
        ret = super().stage()
        self._datum_counter = itertools.count()
        return ret

    def unstage(self):
        #self.settings.trigger_mode.put(0)  # 'Software'
        super().unstage()
        self._datum_counter = None

    def complete(self, *args, **kwargs):
        for resource in self.hdf5._asset_docs_cache:
            self._asset_docs_cache.append(('resource', resource[1]))

        self._datum_ids = []

        num_frames = self.hdf5.num_captured.get()

        for frame_num in range(num_frames):
            for channel_num in self.hdf5.channels:  # Channels (1, 2) as of 03/04/2020
                datum_id = '{}/{}'.format(self.hdf5._resource_uid, next(self._datum_counter))
                datum = {'resource': self.hdf5._resource_uid,
                         'datum_kwargs': {'frame': frame_num,
                                          'channel': channel_num},
                         'datum_id': datum_id}
                self._asset_docs_cache.append(('datum', datum))
                self._datum_ids.append(datum_id)

        return NullStatus()

    def collect(self):
        now = ttime.time()
        print(f'now: {now}')
        for datum_id in self._datum_ids:
            data = {self.name: datum_id}
            yield {'data': data,
                   'timestamps': {key: now for key in data}, 'time': now,  # TODO: use the proper timestams from the mono start and stop times
                   'filled': {key: False for key in data}}

    def collect_asset_docs(self):
        file_plugins = [s for s in self._signals.values() if
                        hasattr(s, 'collect_asset_docs')]
        for p in file_plugins:
            yield from p.collect_asset_docs()
                                
        #items = list(self._asset_docs_cache)
        #self._asset_docs_cache.clear()
        #for item in items:
        #    yield item

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
    roi_names = ['roi{:02}'.format(j) for j in [1, 2, 3, 4, 5, 6, 7]]
    d.rois.read_attrs = roi_names
    d.rois.configuration_attrs = roi_names
    for roi_n in roi_names:
        getattr(d.rois, roi_n).value_sum.kind = 'omitted'

# set up ROI hints for best effort callback
xsp3.channel1.rois.roi01.value.kind = 'hinted'
xsp3.channel1.rois.roi02.value.kind = 'hinted'
xsp3.channel1.rois.roi03.value.kind = 'hinted'
xsp3.channel1.rois.roi04.value.kind = 'hinted'

xsp3.hdf5.warmup()