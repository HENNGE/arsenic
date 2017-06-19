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

.. toctree::
    :maxdepth: 2
    :caption: Tutorials

    tutorials/helloworld


.. toctree::
    :maxdepth: 2
    :caption: How-to Guides

    howto/pytest
    howto/action_chains

.. toctree::
    :maxdepth: 2
    :caption: Reference

    reference/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
