"""
initialize Bluesky framework
"""

__all__ = ['RE', 'db', 'sd', 'peaks','bp', 'bps', 'bpp',
            'np', 'summarize_plan', 'callback_db', ]

from ..session_logs import logger
logger.info(__file__)

import os, sys

def get_md_path():
    md_dir_name = "Bluesky_RunEngine_md"
    if os.environ == "win32":
        home = os.environ["LOCALAPPDATA"]
        path = os.path.join(home, md_dir_name)
    else:       # at least on "linux"
        home = os.environ["HOME"]
        path = os.path.join(home, ".config", md_dir_name)
    return path

old_md = None
md_path = get_md_path()

if not os.path.exists(md_path):
    logger.info(
        "New directory to store RE.md between sessions: %s", 
        md_path)
    os.makedirs(md_path)
    from bluesky.utils import get_history
    old_md = get_history()

from bluesky import RunEngine
RE = RunEngine()
from bluesky.utils import PersistentDict 
RE.md = PersistentDict(md_path)
if old_md is not None:
    logger.info('migrating RE.md storage to PersistentDict')
    RE.md.update(old_md)

# keep track of callback subscriptions
callback_db = {}

# set up databroker
import databroker
db = databroker.Broker.named('mongoCat')
callback_db['Broker'] = RE.subscribe(db.insert)

# Set up SupplementalData.
from bluesky import SupplementalData
sd = SupplementalData()
RE.preprocessors.append(sd)

# Add a progress bar.
from bluesky.utils import ProgressBarManager
pbar_manager = ProgressBarManager()
RE.waiting_hook = pbar_manager

# Register bluesky IPython magics.
from IPython import get_ipython
from bluesky.magics import BlueskyMagics
get_ipython().register_magics(BlueskyMagics)
get_ipython().magic("automagic 0") # Turn off automagic

# Set up the BestEffortCallback.
from bluesky.callbacks.best_effort import BestEffortCallback
bec = BestEffortCallback()
callback_db['BestEffortCallback'] = RE.subscribe(bec)
peaks = bec.peaks  # just as alias for less typing
bec.disable_baseline()


# convenience imports
import bluesky.plans as bp
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
import numpy as np

# diagnostics
from bluesky.utils import ts_msg_hook
#RE.msg_hook = ts_msg_hook
from bluesky.simulators import summarize_plan   