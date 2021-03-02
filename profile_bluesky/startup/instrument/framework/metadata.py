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
if 'proposal_id' not in RE.md:
    RE.md['proposal_id'] = 'testing'
RE.md['pid'] = os.getpid() # process ID

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

def show_md():
    print('Persistent Metadata --------------------')
    for key, item in RE.md.items():
        print(f'{key}: {item}')

    print('----------------------------------------')

def update_md(key, item):
    print('Update persistent metadata with the syntax: RE.md["key"]="item"')

def new_user():
    print('Updating metadata for new user...')
    prop = input('Proposal id: ')
    operator = input('Operator: ')

    # update md
    RE.md['proposal_id'] = prop
    RE.md['operator'] = operator
    