==========================
Frequently Asked Questions
==========================

Q: Can we run Bluesky in a jupyter notebook? It's python after all.

A: While a notebook is a convenient way to run data analysis, 
the ability to run cells out of order is dangerous in a beamline setting.  
Order is important, and limiting commands to a more traditional console was an 
intentional choice.  If you're looking for your past commands, you can either 
check the history or search for past commands with ``Ctrl+R``.

Q: Where is my data?

A: 


Q: Where are the log files?

A: The Ipython console stores log files in the directory it's started in.
``<start dir> / .logs``.  These log files record the command history, but not output.  