Unofficial Brain.fm Python Client (3.5+)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``Connection`` class exposes three operations: ``login``, ``list_stations``, and ``get_token``.
Please open an issue if there's another operation you need.

This client requires Python 3.5+.

================
 CLI Quickstart
================

::

    $ pip install brainfm
    $ brain init
    Email: user@gdomain.com
    Password: <hidden>
    Repeat for confirmation: <hidden>

    Add the following to your .profile, .bashrc, or equivalent:

        export BRAINFM_SID="s%3...s0xo"
    $ # <commands to modify and reload profile>
    $ brain play 300

====================
 Library Quickstart
====================

::

    pip install brainfm

.. code-block:: pycon

    >>> import brainfm
    >>> client = brainfm.Connection()
    >>> client.login("your@email.here", "hunter2")
    >>> client.list_stations()
    [{'name': 'Cinematic Music Focus', 'id': 300,
      'string_id': 'explore.focus.cinematic'},
     {'name': 'Beach Focus', 'id': 53,
      'string_id': 'explore.focus.beach'},
     ...]
    >>> token = client.get_token(53)
    >>> token
    '63f4b59b-93f4-45e6-b0c2-eb6b1582fb96'
    >>> client.make_stream_url(token)
    'https://stream.brain.fm/?tkn=63f4b59b-93f4-45e6-b0c2-eb6b1582fb96'

Now, open the stream using that token::

    https://stream.brain.fm/?tkn=63f4b59b-93f4-45e6-b0c2-eb6b1582fb96

=====
 CLI
=====

Expects an environment variable named `BRAINFM_SID` to exist.
You can use `brain init` to generate one:

::

    $ brain init
    Email: user@gdomain.com
    Password: <hidden>
    Repeat for confirmation: <hidden>

    Add the following to your .profile, .bashrc, or equivalent:

        export BRAINFM_SID="s%3...s0xo"

Usage::

    $ brain ls
    +Available Stations------------+---------------------------+
    | id  | name                   | string_id                 |
    +-----+------------------------+---------------------------+
    | 34  | Relaxed Focus          | explore.relaxed           |
    | 53  | Beach Focus            | explore.focus.beach       |
    | 54  | Chimes & Bowls Focus   | explore.focus.bells       |
    | 55  | Electronic Music Focus | explore.focus.electronic  |
    | ... | ...                    | ...                       |
    | 262 | Wind Relax             | explore.relax.wind        |
    | 300 | Cinematic Music Focus  | explore.focus.cinematic   |
    +-----+------------------------+---------------------------+

    $ brain gt 60
    3ff0eab0-a5f6-11e6-a5c2-f11c700a6178

    $ brain play 60
    # opens a browser at:
    #   https://stream.brain.fm/?tkn=3ff0eab0-a5f6-11e6-a5c2-f11c700a6178

============
 User-Agent
============

By default the user agent is ``github.com/numberoverzero/brainfm``
followed by the project ``__version__``.
There is also a packaged browser-like user-agent:

.. code-block:: pycon

    >>> client = brainfm.Connection(...)
    >>> client.user_agent = brainfm.BROWSER

Instead of filtering, maybe this will be a good metric
for customer interest in an official API :heart:
