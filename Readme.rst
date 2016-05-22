Trakt.tv Python3 API
--------------------

.. image:: https://img.shields.io/pypi/trakt_aiohttp.svg
   :target:  https://pypi.python.org/pypi/trakt_aiohttp/

.. image:: https://img.shields.io/travis/XayOn/trakt_aiohttp.svg
   :target: https://travis-ci.org/XayOn/trakt_aiohttp


This project covers a basic python3 Trakt API with *device* auth
using aiohttp.

To use it, have a look at __init__.py's Trakt class.

::

    async def foo():
        trakt = Trakt(CID, CSECRET)
        watchlist = await trakt.watchlist()
        calendar_mine = await trakt.calendars_shows('my', 'new',
            '2015-10-20', 7)

Have a look at the Trakt API docs at http://docs.trakt.apiary.io/#reference


Features
++++++++

- Unit tests using mockup apiary server
- Aiohttp
- Python3.5 style coroutines
- Implemented methods:
  - Calendar show query
  - Calendar movie query
  - Checkin API
  - Genre listing
  - Translations API
  - Movies listing by sorting
  - Shows listing by sorting
  - Seasons and episodes listing
  - Single episode info

TODO
++++

- Proper narrative documentation
- Search API

