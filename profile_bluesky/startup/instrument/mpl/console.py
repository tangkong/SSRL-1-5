"""
Configure matplotlib in interactive mode for ipython console 
"""
# list of public objects imported by "import *"
__all__ = ['plt',]

from ..session_logs import *
logger.info(__file__)

import matplotlib.pyplot as plt
plt.ion()