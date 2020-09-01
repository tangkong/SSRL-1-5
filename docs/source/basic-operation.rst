===========================
Basic Operation in Bluesky
===========================

.. Note:: Bluesky provides a thorough tutorial_.  The content here should be 
    taken as a quick reference or crib sheet.  

.. _tutorial: https://nsls-ii.github.io/bluesky/tutorial.html


Commands are grouped into "plans".  All plans in the Bluesky interface must be
passed to the ``RunEngine``, usually accessible by the variable ``RE``.

.. code-block:: ipython

    In [1]: RE( <plan> )
    <plan output>

The ``RunEngine`` then takes care of orchestrating the experiment, sending 
signals to devices, and storing data.  

Standard plans
==============
Standard plans are stored under the variable ``bp``, which stands for 
``bluesky.plans``.  Most operations should eventually be folded into customized 
plans, but these will get the job done until then. Detailed documentation on 
Bluesky's pre-assembled plans can be found 
`here <https://nsls-ii.github.io/bluesky/plans.html>`__.
Examples here will utilize basic Bluesky plans, which 
may be too verbose for the average user.  More specialized plans will be covered
in the :doc:`plans` section


Scanning detectors: ``bp.scan``
-------------------------------
The scan plan takes in a list of detectors to measure, a motor to scan, a start 
coordinate, stop coordinate, and number of measurements. 

.. code-block:: ipython

    In [3]: RE(bp.scan([det], motor, -1, 1, 5)) 
    Transient Scan ID: 1     Time: 2020-08-27 15:57:41
    Persistent Unique Scan ID: '2a328312-e6e8-4127-a815-05f7020c6b2a'
    New stream: 'primary'
    +-----------+------------+------------+------------+
    |   seq_num |       time |      motor |        det |
    +-----------+------------+------------+------------+
    |         1 | 15:57:41.5 |     -1.000 |      0.607 |
    |         2 | 15:57:41.5 |     -0.500 |      0.882 |
    |         3 | 15:57:41.8 |      0.000 |      1.000 |
    |         4 | 15:57:41.8 |      0.500 |      0.882 |
    |         5 | 15:57:41.9 |      1.000 |      0.607 |
    +-----------+------------+------------+------------+
    generator scan ['2a328312'] (scan num: 1)

    Out[3]: ('2a328312-e6e8-4127-a815-05f7020c6b2a',)


One can also perform a relative scan with ``bp.rel_scan``

.. code:: ipython

    In [1]: .... # TO-DO Grab example relative scan


Move motors: ``bps.mv``
-----------------------
The one exception to the rule is the "move" plan, which is a "plan_stub" used 
as a component of other plans.  As such it is accessed via ``bps.mv``.

.. just use dumb code block directive to format correctly.  Ipython directive
.. tries to run the code

.. code-block:: ipython

    In [1]: RE(bps.mv(motor, 2))
    Out[1]: ()


Can also access via "ipython magic" shortcuts

.. code-block:: ipython

    In [2]: %mv motor 2
