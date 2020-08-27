===========================
Basic Operation in Bluesky
===========================

.. Note:: Bluesky provides a thorough tutorial_.  The content here should be 
    taken as a quick reference or crib sheet.  

.. _tutorial: https://nsls-ii.github.io/bluesky/tutorial.html


Commands are grouped into "plans".  All plans in the Bluesky interface must be
 passed to the ``RunEngine``, usually accessible by the variable ``RE``.::

    >>> RE( <plan> )
    <plan output>

The ``RunEngine`` then takes care of orchestrating the experiment, sending 
signals to devices, and storing data.  

Standard plans
--------------
Standard plans are stored under the variables ``bp`` or ``bps``, which stand for 
``bluesky.plans`` and ``bluesky.plan_stubs`` respectively

``bp.scan``
+++++++++++