Arsenic with pytest
###################

A common usage of webdrivers is for testing web applications. Thanks to the
async nature of arsenic, you can test your async web applications from the same
process and thread as you run your application.

In this guide, we will have a small `aiohttp`_ based web application and test
it using `pytest`_ and `pytest-asyncio`_.

Prerequisites
*************

This guide assumes you are familiar with pytest and it's terminology.

Setup
*****

You should already have Firefox and Geckodriver installed. Make sure your
geckodriver is in your ``PATH``.

Create a virtualenv and install the required dependencies:

    python3.6 -m venv env
    env/bin/pip install --upgrade pip
    env/bin/pip install --pre arsenic
    env/bin/pip install pytest-asyncio

App
***

Our app will have a single handler:

.. literalinclude:: test_pytest.py
    :lines: 10-27


Fixture
=======

To make our app easily available in tests, we'll write a pytest fixture which
runs our app and provides the base url to it, since we will run it on a random
port:

.. literalinclude:: test_pytest.py
    :lines: 30-43


Arsenic Fixture
***************

We will also write a fixture for arsenic, which depends on the app fixture and
provides a running Firefox session bound to the app:

.. literalinclude:: test_pytest.py
    :lines: 46-56


Test
****

We will add a simple test which shows that the title on a GET request is
Hello World, and if we submit the form it will become Hello followed by what
we put into the text field:

.. literalinclude:: test_pytest.py
    :lines: 59-70

Putting it all together
***********************

For this all to work, we'll need a few imports:

.. literalinclude:: test_pytest.py
    :lines: 1-5

And we also need to mark the file as asyncio for pytest to support async
functions:

.. literalinclude:: test_pytest.py
    :lines: 7

Now to put it all together, create a file called ``test_pytest.py`` and insert
the following code:


.. literalinclude:: test_pytest.py
    :emphasize-lines: 59-70

To run it, simply execute ``pytest test_pytest.py``.


.. _aiohttp: https://aiohttp.readthedocs.org/en/latest/
.. _pytest: https://docs.pytest.org/en/latest/
.. _pytest-asyncio: https://github.com/pytest-dev/pytest-asyncio


