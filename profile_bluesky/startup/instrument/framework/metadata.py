__all__ = ['RE',]

from ..session_logs import logger
logger.info(__file__)

import ssrltools
import bluesky
import databroker
from datetime import datetime
import epics
import getpass
import h5py
import matplotlib
import numpy
import ophyd
import os
import pymongo
import socket

from .initialize import RE

# Set up default metadata

RE.md['beamline_id'] = 'SSRL 1-5 HiTp'
RE.md['proposal_id'] = 'testing'
RE.md['pid'] = os.getpid()

HOSTNAME = socket.gethostname() or 'localhost' 
USERNAME = getpass.getuser() or 'SSRL 1-5 HiTp user' 
RE.md['login_id'] = USERNAME + '@' + HOSTNAME

# useful diagnostic to record with all data
RE.md["versions"] = dict(
    bluesky = bluesky.__version__,
    ophyd = ophyd.__version__,
    databroker = databroker.__version__,
    ssrltools = ssrltools.__version__,
    epics = epics.__version__,
    numpy = numpy.__version__,
    matplotlib = matplotlib.__version__,
    pymongo = pymongo.__version__,
)