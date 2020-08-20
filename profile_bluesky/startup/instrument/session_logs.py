"""
configure session logging 
"""

__all__ = ['logger',]

import logging
import os

_log_path = os.path.join(os.getcwd(), ".logs")
if not os.path.exists(_log_path):
    os.mkdir(_log_path)

CONSOLE_TO_FILE = os.path.join(_log_path, 'ipython_console.log')

# start logging console to file
from IPython import get_ipython
_ipython = get_ipython()
_ipython.magic(f'logstart -o -t {CONSOLE_TO_FILE} rotate')

# create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.info('#'*60 + " startup")
logger.info('logging started')
logger.info(f'logging level = {logger.level}')