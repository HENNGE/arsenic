Concepts
########

.. _Service:

Service
*******

A Service is responsible for starting and stopping browser instances. An example
of a Service is `geckodriver`_.

.. _Engine:

Engine
******

An Engine is a wrapper around a Python async framework which powers arsenic.
arsenic comes with builtin engines for the `tornado`_ and `aiohttp`_ frameworks.

.. _Browser:

Browser
*******

A Browser is an actual browser which is run by a :ref:`Service`.

.. _Session:

Session
*******

A Session is an instance of a :ref:`Browser` with which we can interact.


Summary
*******

We run a :ref:`Service` using an :ref:`Engine` to start a :ref:`Browser` and get
a :ref:`Session` to interact with.


.. _geckodriver: https://github.com/mozilla/geckodriver
.. _tornado: https://tornado.readthedocs.io/en/stable/
.. _aiohttp: https://aiohttp.readthedocs.io/en/stable/
