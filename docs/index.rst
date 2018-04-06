.. arsenic documentation master file, created by
   sphinx-quickstart on Tue May 23 17:11:19 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to arsenic's documentation!
###################################


.. warning::

    While this library is asynchronous, web drivers are **not**. You must call
    the APIs in sequence. The purpose of this library is to allow you to control
    multiple web drivers asynchronously or to use a web driver in the same thread
    as an asynchronous web server.


Arsenic is a library that allows you to control a web browser from async Python
code. Use cases include testing of web applications, load testing, automating
websites, web scraping or anything else you need a web browser for. It uses real
web browsers using the `Webdriver`_ specification.

While it is built on top of `aiohttp`_, it can be used from any asyncio-compatible
framework, such as `Tornado`_.


You can find the code of arsenic on `Github`_ and `PyPI`_.


.. toctree::
    :maxdepth: 2
    :caption: Tutorials

    tutorials/helloworld


.. toctree::
    :maxdepth: 2
    :caption: How-to Guides

    howto/pytest
    howto/windows
    howto/action_chains

.. toctree::
    :maxdepth: 2
    :caption: Reference

    reference/supported-browsers
    reference/index


.. toctree::
    :maxdepth: 2
    :caption: Development

    development/testing



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _Webdriver: https://w3c.github.io/webdriver/webdriver-spec.html
.. _aiohttp: https://aiohttp.readthedocs.io/en/stable/
.. _tornado: https://tornado.readthedocs.io/en/stable/
.. _Github: https://github.com/hde/arsenic
.. _PyPI: https://pypi.org/project/arsenic/
