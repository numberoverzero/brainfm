Unofficial Brain.fm Python Client (3.5+)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``Connection`` class exposes four operations: ``login``,
``list_stations``, ``get_token`` and ``make_stream_url``.  Please open an
issue if there's another operation you need.

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
        export BRAINFM_STREAM_ENDPOINT="https://..."

    $ # ... commands to modify and reload profile ...
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

You must pass an sid with ``--sid`` or define an environment variable
``BRAINFM_SID``.  You can use ``brain init`` to generate one:

::

    $ brain init
    Email: user@gdomain.com
    Password: <hidden>
    Repeat for confirmation: <hidden>

    Add the following to your .profile, .bashrc, or equivalent:

        export BRAINFM_SID="s%3...s0xo"
        export BRAINFM_STREAM_ENDPOINT="https://..."

While setting ``BRAINFM_STREAM_ENDPOINT`` is not strictly necessary, the
cli is faster when either the env var is defined or you provide the endpoint
explicitly: ``brain --stream-endpoint=... ls``

Usage::

    $ brain ls
    +Playable Stations-------------+-----------------------+-------- +
    | id  | name                   | string_id             | length  |
    +-----+------------------------+-----------------------+-------- +
    | 32  | Quick Relax            | relax.justrelax15min  | 15 mins |
    | 34  | Relaxed Focus          | explore.relaxed       | 30 mins |
    | 35  | Focus                  | focus.3               | 30 mins |
    | 36  | Sleep                  | sleep                 | 45 mins |
    | ... | ...                    | ...                   | ...     |
    | 540 | Study Focus            | explore.focus.study   | 30 mins |
    | 541 | LoFi Focus             | explore.focus.lowfi   | 30 mins |
    +-----+------------------------+-----------------------+-------- +

    $ brain ls -a
    +All Stations------------------+-----------------------+-------- +
    | id  | name                   | string_id             | length  |
    +-----+------------------------+-----------------------+-------- +
    | 0   | Favorites              | None                  | None    |
    | 32  | Quick Relax            | relax.justrelax15min  | 15 mins |
    | 34  | Relaxed Focus          | explore.relaxed       | 30 mins |
    | ... | ...                    | ...                   | ...     |
    | 46  | Explore                | explore               | None    |
    | 47  | Explore Relax          | explore.relax         | None    |
    | ... | ...                    | ...                   | ...     |
    | 541 | LoFi Focus             | explore.focus.lowfi   | 30 mins |
    +-----+------------------------+-----------------------+-------- +

    $ brain gt 60
    3ff0eab0-a5f6-11e6-a5c2-f11c700a6178

    $ brain play 60
    # opens a browser at:
    #   https://stream.brain.fm/?tkn=3ff0eab0-a5f6-11e6-a5c2-f11c700a6178

--------------------
 Override Endpoints
--------------------

From the cli you can override the api and stream endpoints with
``--api-endpoint`` and ``--stream-endpoint`` respectively.  This is useful
when the service switches endpoints but this library hasn't been updated to
match.

You can also provide these as env variables
``BRAINFM_API_ENDPOINT`` and ``BRAINFM_STREAM_ENDPOINT``

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
