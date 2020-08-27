"""
configure for data collection in a console session
"""

from .session_logs import *
logger.info(__file__)

from .mpl import *

logger.info("bluesky framework")

from .framework import *
from .devices import *
from .callbacks import *
from .plans import *

#from apstools.utils import *

# ensure nothing clobbered our logger
from .session_logs import logger

logger.info(
    "Disabling log output to the console now."
    " Log output will still be recoreded in log files."
    " Re-enable with this console-only command: \n"
    "      logger.addHandler(console_log_writer)"
    )

logger.info('Bluesky startup is complete')