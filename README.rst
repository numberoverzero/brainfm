Unofficial Brain.fm Python Client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(very few commands implemented)

============
 Quickstart
============

::

    pip install brainfm

.. code-block:: pycon

    >>> import brainfm
    >>> client = brainfm.Connection("your@email.here", "hunter2")
    >>> client.get_stations()
    [{'name': 'Cinematic Music Focus', 'station_id': 300,
      'canonical_name': 'explore.focus.cinematic'},
     {'name': 'Beach Focus', 'station_id': 53,
      'canonical_name': 'explore.focus.beach'},
     ...]
    >>> client.get_station(station_id=53)
    {'name': 'Beach Focus', 'station_id': 53, 'canonical_name': 'explore.focus.beach'}
    >>> client.get_token(station_id=53)
    {'session_token': '63f4b59b-93f4-45e6-b0c2-eb6b1582fb96',
     'group': 'FOCUS', 'name': 'Beach Focus', 'session_id': 121,
     'station_id': 53}

Now, open the stream using that token::

    https://stream.brain.fm/?tkn=63f4b59b-93f4-45e6-b0c2-eb6b1582fb96


============
 User-Agent
============

By default the user agent is ``github.com/numberoverzero/brain.fm`` followed by the project ``__version__``.
There is also a packaged browser-like user-agent:

.. code-block:: pycon

    >>> client = brainfm.Connection(...)
    >>> client.user_agent = brainfm.BROWSER

Instead of filtering, maybe this will be a good metric for customer interest in an official API :heart:
