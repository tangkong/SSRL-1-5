"""
Bluesky plans to tune various axes and stages

credit to apstools
"""

__all__ = [ 'tune', 'tune_params' ]

from ..session_logs import logger
logger.info(__file__)

import bluesky.plan_stubs as bps
import bluesky.plans as bp
from ophyd import Kind
import time

from bluesky.preprocessors import inject_md_decorator, subs_decorator
from bluesky.callbacks.fitting import PeakStats

# devices to tune
from ..devices.stages import s_stage
from ..devices.misc_devices import shutter
from ..framework import RE

tune_params = {
    's_stage_px':{ 'width': 20, 'num': 20, 'peak_choice': 'com'},
    's_stage_py':{ 'width': 20, 'num': 20, 'peak_choice': 'com'},
    's_stage_pz':{ 'width': 20, 'num': 20, 'peak_choice': 'com'},

    'motor': {'width': 4, 'num': 20, 'peak_choice': 'com'}
}

peak_choices = {'com', 'cen', 'max'}


def tune(signal, motor, width=None, num=None, peak_choice=None, md=None):
    """tune an axis, single pass.  Scans axis centered at current position
    from ``-width/2`` to ``width/2`` with ``num`` observations
    """
    # set up parameters for tune 
    name = motor.name

    try: # if both exist, take provided parameter
        # if argument defined, short circuting ignores KeyError
        width = width or tune_params[name]['width']
        num = num or tune_params[name]['num']
        peak_choice = peak_choice or tune_params[name]['peak_choice']
    except KeyError as ke:
        msg = f'Tuning parameters not defined for provided motor: {name}' 
        raise KeyError(msg)

    initial_position = motor.position

    # TO-DO Check to make sure params are in dictionary, abort if not
    
    # gather metadata
    _md = {'plan_name': motor.name + '.tune',
           'motors': motor.name,
           'detectors': signal.name,
           'hints': dict(
               dimensions = [ ([motor.name], 'primary')]
           )
    }
    _md.update(md or {})
    
    peak_stats = PeakStats(x=motor.name, y=signal.name)

    # start plans
    @subs_decorator(peak_stats)
    @inject_md_decorator(_md)
    def _scan(md=None):

        yield from bp.rel_scan([signal], motor, -width/2, width/2, num)

        # Grab final position from subscribed peak_stats
        valid_peak = peak_stats.max[-1] >= (4 * peak_stats.min[-1])
        if peak_stats.max is None:
            valid_peak = False

        final_position = initial_position
        if valid_peak: # Condition for finding a peak
            if peak_choice == 'cen':
                final_position = peak_stats.cen
            elif peak_choice == 'com':
                final_position = peak_stats.com

        yield from bps.mv(motor, final_position)

    return (yield from _scan())