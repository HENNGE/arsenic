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

Waiting
*******

Quite often you will need to wait for the browser context to be in a certain state.
To do so, you can use :py:meth:`arsenic.session.Session.wait` which is a low
level API to wait for certain conditions. It takes two or more arguments: A timeout
as an integer or float of seconds to wait, a coroutine callback to check if the
condition is met and an optionally exception classes which should be ignored.

The callback should return a truthy value to indicate the condition is met.

For extra convenience, there are built-in APIs to wait for an element to appear
and an element to go away, :py:meth:`arsenic.Session.wait_for_element` and
:py:meth:`arsenic.Session.wait_for_element_gone` respectively. Both take a
timeout as an integer or float of seconds as first argument and a CSS selector
as second argument. :py:meth:`arsenic.Session.wait_for_element` returns the
element after it was found.

An example to use the generic wait API to wait up to 5 seconds for an alert to
show up would be::

    alert_text = await session.wait(
        5,
        session.get_alert_text,
        NoSuchAlert
    )
