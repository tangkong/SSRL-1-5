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

    In [4]: %mov motor 1

    In [5]: RE(bp.rel_scan([det], motor, -1, 1, 5))


    Transient Scan ID: 16     Time: 2020-09-17 18:40:56
    Persistent Unique Scan ID: '223510b1-fe9e-4b12-b427-70e5370ed86c'
    New stream: 'baseline'
    New stream: 'primary'
    +-----------+------------+------------+------------+
    |   seq_num |       time |      motor |        det |
    +-----------+------------+------------+------------+
    |         1 | 18:40:56.7 |      0.000 |      1.000 |
    |         2 | 18:40:56.7 |      0.500 |      0.882 |
    |         3 | 18:40:56.8 |      1.000 |      0.607 |
    |         4 | 18:40:56.8 |      1.500 |      0.325 |
    |         5 | 18:40:56.8 |      2.000 |      0.135 |
    +-----------+------------+------------+------------+
    generator rel_scan ['223510b1'] (scan num: 16)
    Out[5]: ('223510b1-fe9e-4b12-b427-70e5370ed86c',)

Scanning a grid of points: ``bp.grid_scan``
-------------------------------------------
Relevant to High Throughput operations at 1-5 is the grid scan plan.  This plan 
scans multiple motors, with the option to either raster (default) or snake along 
axes.  Snaking will be more time efficient, but the time saved depends on 
factors such as motor speed 
More detailed descriptions of these plans can be found `here`_.  `Snaking explained`_


.. _here: https://nsls-ii.github.io/bluesky/plans.html#multi-dimensional-scans
.. _Snaking explained: https://nsls-ii.github.io/bluesky/tutorial.html#scan-multiple-motors-in-a-grid

.. code-block:: ipython

    In [31]: RE(bp.grid_scan([det],
        ...:  motor1, -1, 1, 3,
        ...:  motor2, -3, 3, 7, True))


    Transient Scan ID: 17     Time: 2020-09-17 18:55:11
    Persistent Unique Scan ID: 'd25cc1c3-a4bb-45b4-aabe-83379c8e9e18'
    New stream: 'baseline'
    New stream: 'primary'
    +-----------+------------+------------+------------+------------+
    |   seq_num |       time |     motor1 |     motor2 |        det |
    +-----------+------------+------------+------------+------------+
    |         1 | 18:55:11.1 |     -1.000 |     -3.000 |      0.607 |
    |         2 | 18:55:11.2 |     -1.000 |     -2.000 |      0.607 |
    |         3 | 18:55:11.2 |     -1.000 |     -1.000 |      0.607 |
    |         4 | 18:55:11.3 |     -1.000 |      0.000 |      0.607 |
    |         5 | 18:55:11.3 |     -1.000 |      1.000 |      0.607 |
    |         6 | 18:55:11.3 |     -1.000 |      2.000 |      0.607 |
    |         7 | 18:55:11.6 |     -1.000 |      3.000 |      0.607 |
    |         8 | 18:55:11.6 |      0.000 |      3.000 |      0.607 |
    |         9 | 18:55:11.6 |      0.000 |      2.000 |      0.607 |
    |        10 | 18:55:11.6 |      0.000 |      1.000 |      0.607 |
    |        11 | 18:55:11.6 |      0.000 |      0.000 |      0.607 |
    |        12 | 18:55:11.6 |      0.000 |     -1.000 |      0.607 |
    |        13 | 18:55:11.6 |      0.000 |     -2.000 |      0.607 |
    |        14 | 18:55:11.6 |      0.000 |     -3.000 |      0.607 |
    |        15 | 18:55:11.6 |      1.000 |     -3.000 |      0.607 |
    |        16 | 18:55:11.7 |      1.000 |     -2.000 |      0.607 |
    |        17 | 18:55:11.7 |      1.000 |     -1.000 |      0.607 |
    |        18 | 18:55:11.7 |      1.000 |      0.000 |      0.607 |
    |        19 | 18:55:11.7 |      1.000 |      1.000 |      0.607 |
    |        20 | 18:55:11.7 |      1.000 |      2.000 |      0.607 |
    |        21 | 18:55:11.7 |      1.000 |      3.000 |      0.607 |
    +-----------+------------+------------+------------+------------+
    generator grid_scan ['d25cc1c3'] (scan num: 17)
    Out[31]: ('d25cc1c3-a4bb-45b4-aabe-83379c8e9e18',)


Grid scans: ``bp.grid_scan``
----------------------------
Scanning over an array of samples arranged in a grid is handled by the 
'grid scan' plan.  A more complete discussion can be found on the official 
`documentation <https://nsls-ii.github.io/bluesky/tutorial.html#scan-multiple-motors-in-a-grid>`__


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

Convenience Functions
=====================

Motor position summary: `%wa`
-----------------------------

.. code-block:: ipython

    In [1]: %wa
    motors
        Positioner                     Value       Low Limit   High Limit  Offset
        motor                          0           AttributeError AttributeError AttributeError
        motor1                         0           AttributeError AttributeError AttributeError
        motor2                         0           AttributeError AttributeError AttributeError

        Local variable name                    Ophyd name (to be recorded as metadata)
        motor                                  motor
        motor1                                 motor1
        motor2                                 motor2


Accessing saved data
====================
You can access saved data through the databroker instance, which should be 
accessible as ``db`` in the bluesky sesison.  Some standard patterns are 
demonstrated below: 
`Official Documentation <https://nsls-ii.github.io/bluesky/tutorial.html#aside-access-saved-data>`__

.. code-block:: ipython

    In [19]: uid = RE(bp.scan([det], motor, -1, 1, 5))


    Transient Scan ID: 15     Time: 2020-09-17 18:13:03
    Persistent Unique Scan ID: 'e2d02570-9b8f-4254-b205-107ba990d740'
    New stream: 'baseline'
    New stream: 'primary'
    +-----------+------------+------------+------------+
    |   seq_num |       time |      motor |        det |
    +-----------+------------+------------+------------+
    |         1 | 18:13:03.4 |     -1.000 |      0.607 |
    |         2 | 18:13:03.5 |     -0.500 |      0.882 |
    |         3 | 18:13:03.5 |      0.000 |      1.000 |
    |         4 | 18:13:03.5 |      0.500 |      0.882 |
    |         5 | 18:13:03.5 |      1.000 |      0.607 |
    +-----------+------------+------------+------------+
    generator scan ['e2d02570'] (scan num: 15)

    In [20]: db[-1].table()  # -1 designates the last run.  -2 would be second most recent, and so on.
    Out[20]: 
                                    time       det  motor  motor_setpoint
    seq_num                                                               
    1       2020-09-18 01:13:03.437488556  0.606531   -1.0            -1.0
    2       2020-09-18 01:13:03.519411087  0.882497   -0.5            -0.5
    3       2020-09-18 01:13:03.561402082  1.000000    0.0             0.0
    4       2020-09-18 01:13:03.569704294  0.882497    0.5             0.5
    5       2020-09-18 01:13:03.576864004  0.606531    1.0             1.0

    In [24]: db[-1].table('baseline')  # we have set up bluesky to take baseline measurements before and after each run
    Out[24]: 
                                    time  s_stage_px  ...  s_stage_th  s_stage_th_user_setpoint
    seq_num                                            ...                                      
    1       2020-09-18 01:13:03.422709942        12.0  ...         1.0                       1.0
    2       2020-09-18 01:13:03.589560270        12.0  ...         1.0                       1.0

    [2 rows x 13 columns]

For those familiar with python data analysis, the ``db[-1].table()`` returns a 
familiar ``pandas.DataFrame`` object.  

Searching the DataBroker:
-------------------------
One of the key advantages of the Bluesky data collection system is the ability
to search data quickly via saved metadata.  Again for a more thorough discussion,
look `here <https://blueskyproject.io/databroker/v1/tutorial.html#searching>`__.

To search DataBroker based on metadata, use parentheses:

.. code:: python

    # Search by plan name.
    headers = db(plan_name='scan')

    # Search for runs involving a motor with the name 'eta'.
    headers = db(motor='eta')

    # Search for runs operated by a given user---assuming this metadata was
    # recorded in the first place!
    headers = db(operator='Dan')

    # Search by time range. (These keywords have a special meaning.)
    headers = db(since='2015-03-05', until='2015-03-10')

To search DataBroker based on relative indexing or unique id, you can use square
brackets:

.. code:: python

    # Get the most recent run.
    header = db[-1]

    # Get the fifth most recent run.
    header = db[-5]

    # Get a list of all five most recent runs, using Python slicing syntax.
    headers = db[-5:]

    # Get a run whose unique ID ("RunStart uid") begins with 'x39do5'.
    header = db['x39do5']

    # Get a run whose integer scan_id is 42. Note that this might not be
    # unique. In the event of duplicates, the most recent match is returned.
    header = db[42]

Managing Metadata 
=================
Metadata is stored with each run, and can be set either for a single run or for 
all future runs.  For a more thorough discussion, look 
`here <https://blueskyproject.io/bluesky/metadata.html>`__ for the full 
documentation.  

Per-run metadata
----------------
Information such as sample name or operational note can be added only to the current 
plan.  One-time metadata can be added directly to the `RE()` call, and will be 
propogated to all runs in the plan:

.. code-block:: ipython 

    In [1]: RE(plan(), sample_id='A', purpose='calibration')

Persistent metadata
-------------------
For information pertaining to all runs in a beamtime, metadata can be recorded 
persistently.  

To see the current metadata dictionary:

.. code-block:: ipython

    In [8]: show_md()
    Persistent Metadata --------------------
    beamline_id: SSRL 1-5 HiTp
    scan_id: 6
    login_id: b_spec@bluedevlx.slac.stanford.edu
    pid: 28034
    versions: {'bluesky': '1.6.6', 'ophyd': '1.5.3', 'databroker': '1.1.0', 'ssrltools': '0.1', 'epics': '3.4.2', 'numpy': '1.19.1', 'matplotlib': '3.3.1', 'pymongo': '3.11.0'}
    proposal_id: testing
    ----------------------------------------

Setting items in this metadata dictionary follows standard python dictionary 
syntax.  This metadata will be retained across ipython session restarts:

.. code-block:: ipython

    In [10]: RE.md['operator']='roberttk'

    In [11]: show_md()
    Persistent Metadata --------------------
    beamline_id: SSRL 1-5 HiTp
    scan_id: 6
    login_id: b_spec@bluedevlx.slac.stanford.edu
    pid: 28034
    operator: roberttk
    versions: {'bluesky': '1.6.6', 'ophyd': '1.5.3', 'databroker': '1.1.0', 'ssrltools': '0.1', 'epics': '3.4.2', 'numpy': '1.19.1', 'matplotlib': '3.3.1', 'pymongo': '3.11.0'}
    proposal_id: testing
    ----------------------------------------

Viewing metadata
----------------
Most of the useful metadata can be accessed from the 'run_start' document:

.. code-block:: ipython

    In [4]: header = db[-1] # grab header for the last/most recent run

    In [5]: header.start
    Out[5]: 
    {'uid': '882fe013-33c4-4fc8-b345-48a4eacb8c87',
    'time': 1600276751.726932,
    'versions': {'ophyd': '1.5.3', 'bluesky': '1.6.6'},
    'scan_id': 1,
    'plan_type': 'generator',
    'plan_name': 'scan',
    'detectors': ['det'],
    'motors': ['motor'],
    'num_points': 3,
    'num_intervals': 2,
    'plan_args': {'detectors': ["SynGauss(prefix='', name='det', read_attrs=['val'], configuration_attrs=['Imax', 'center', 'sigma', 'noise', 'noise_multiplier'])"],
    'num': 3,
    'args': ["SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
    -1,
    1],
    'per_step': 'None'},
    'hints': {'dimensions': [[['motor'], 'primary']]},
    'plan_pattern': 'inner_product',
    'plan_pattern_module': 'bluesky.plan_patterns',
    'plan_pattern_args': {'num': 3,
    'args': ["SynAxis(prefix='', name='motor', read_attrs=['readback', 'setpoint'], configuration_attrs=['velocity', 'acceleration'])",
    -1,
    1]}}
