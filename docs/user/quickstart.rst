Quickstart
##########


Install
*******

1. Create a Python 3.6 virtual environment
2. Install ``arsenic[aiohttp]`` for ``aiohttp`` support or ``arsenic[tornado]`` for ``tornado`` support.


Scripting
*********

To access example.com and read it's title using firefox and tornado, you could
run the following:

.. literalinclude:: ../examples/tornado/scripting.py


Running that should print ``The Title is: Example Domain``.


Testing
*******


Create an app
=============

Let's create a super simple aiohttp based app. Create a file called ``app.py``
and write this code:

.. literalinclude:: ../examples/aiohttp/app.py

Use arsenic to test the app
===========================

We'll use pytest as our test framework, so you'll need to install ``pytest`` and
``pytest-asyncio``.


Create a file ``test_app.py`` and write the following code:

.. literalinclude:: ../examples/aiohttp/test_app.py

Now if you run ``pytest test_app.py`` arsenic will spawn a Firefox instance and
use it to check that your website is behaving correctly.

