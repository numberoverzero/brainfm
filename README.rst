Unofficial Brain.fm Python Client (3.5+)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Very few commands are currently implemented.  Please open an issue if there's a specific command you need.  If you're up for debugging their interesting wire format, additional details make it easier to implement your request.

This client requires Python 3.5+.

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

=====
 CLI
=====

Needs a credentials file in ~/.brainfm/config with the format::

    {
        "email": "your@email.here",
        "password": "hunter2"
    }

Usage::

    $ brain ls
    +Available Stations------------+---------------------------+
    | id  | name                   | canonical                 |
    +-----+------------------------+---------------------------+
    | 34  | Relaxed Focus          | explore.relaxed           |
    | 53  | Beach Focus            | explore.focus.beach       |
    | 54  | Chimes & Bowls Focus   | explore.focus.bells       |
    | 55  | Electronic Music Focus | explore.focus.electronic  |
    | ... | ...                    | ...                       |
    | 262 | Wind Relax             | explore.relax.wind        |
    | 300 | Cinematic Music Focus  | explore.focus.cinematic   |
    +-----+------------------------+---------------------------+

    $ brain gs 60
    {
        "canonical_name": "explore.focus.wind",
        "name": "Wind Focus",
        "station_id": 60
    }

    $ brain gt 60
    {
        "group": "FOCUS",
        "name": "Wind Focus",
        "session_id": 143,
        "session_token": "3ff0eab0-a5f6-11e6-a5c2-f11c700a6178",
        "station_id": 60
    }

    $ brain play 60
    # opens a browser at:
    #   https://stream.brain.fm/?tkn=3ff0eab0-a5f6-11e6-a5c2-f11c700a6178

============
 User-Agent
============

By default the user agent is ``github.com/numberoverzero/brainfm`` followed by the project ``__version__``.
There is also a packaged browser-like user-agent:

.. code-block:: pycon

    >>> client = brainfm.Connection(...)
    >>> client.user_agent = brainfm.BROWSER

Instead of filtering, maybe this will be a good metric for customer interest in an official API :heart:
