#######
Testing
#######

Basics
******

Native
======

This is the easiest way to get started running the tests. The test runner will try to find all local browsers it supports
and run the tests on them (headlessly when possible). Note that on top of having the browsers (eg Firefox) installed,
you also need their webdriver installed (eg Geckodriver).

* Install `poetry`_.
* Install the test requirements using ``poetry install``.
* Run ``poetry run pytest``.

Docker/CircleCI
===============

* Install the `CircleCI command line tool`_.
* Run ``circleci local execute``

.. warning::

    This will pull a massive (1GB+) docker file. Make sure you have the bandwidth and disk space for this.


Advanced
********

Explicitly specify drivers
==========================

The test suite will try to find the webdrivers and browsers automatically, but sometimes this will fail. You can
specify the location of the drivers yourself via the following environment variables:

* ``GECKODRIVER_BINARY``: Path to the geckodriver
* ``CHROMEDRIVER_BINARY``: Path to the chromedriver
* ``IEDRIVERSERVER_BINARY``: Path to IEDriverServer.exe


Only run tests on one browser
=============================

Use the ``-k`` flag of ``pytest`` to select a specific browser. For example, to only run on chrome, use ``-k chrome_session``.


Testing remote drivers
======================

The test suite is set up to test remotely via Browserstack. To do so, set the following environment variables:

* ``BROWSERSTACK_API_KEY``: Your Browserstack API key.
* ``BROWSERSTACK_LOCAL_IDENTIFIER``: Identifier for your build.
* ``REMOTE_BROWSER``: A JSON encoded object. It requires at least the ``"type"`` key, which is the name of the browser class
    in arsenic. All other keys will be passed to the arsenic browser class.
* ``REMOTE_SERVICE``: URL to the remote service executor. Include the username/password here. Eg ``https://<user>:<pass>@hub.browserstack.com/wd/hub``


Adding a new browser to test
============================

Open the file ``tests/conftest.py``. Add an extra function to the ``params`` list in the ``pytest.fixture`` decorator call for
``async def session``. The function should be an async context manager, which takes the root url to the app to test as an
argument and yields a ``Session``.

.. _CircleCI command line tool: https://circleci.com/docs/2.0/local-jobs/
.. _poetry: https://python-poetry.org/docs/#installation
