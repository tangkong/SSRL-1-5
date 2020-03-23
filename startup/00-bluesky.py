# Following scripts to be run as ipython startup scripts. 
# Add contents to ~/.ipython/yourprofile/startup

"""connect with Bluesky"""

from bluesky import RunEngine
RE = RunEngine()
# from bluesky.utils import PersistentDict 
# RE.md = PersistentDict('./metadata.md')

# from ssrltools.utils import setup_user_metadata
# user_md = setup_user_metadata()
# RE.md.update(user_md)

# Import matplotlib and put it in interactive mode.
import matplotlib.pyplot as plt
plt.ion()

# Optional: set any metadata that rarely changes. in 60-metadata.py

# convenience imports
from bluesky.callbacks import *
import bluesky.plans as bp
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from time import sleep
import numpy as np
import bluesky.magics


# diagnostics
from bluesky.utils import ts_msg_hook
#RE.msg_hook = ts_msg_hook
from bluesky.simulators import summarize_plan   