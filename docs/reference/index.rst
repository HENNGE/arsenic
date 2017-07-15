API Reference
#############


Main APIs
*********

.. py:module:: arsenic

.. py:function:: get_session(service, browser, bind=''):

    Async context manager API to start/stop a browser session.

    :param service: The service which manages the browser instance.
    :type service: :py:class:`arsenic.services.Service`
    :param browser: The browser to start.
    :type browser: :py:class:`arsenic.browsers.Browser`
    :param str bind: Optional URL to bind the browser to.
    :return: An async context manager.


.. py:function:: start_session(service, browser, bind=''):

    Coroutine to start new session.

    :param service: The service which manages the browser instance.
    :type service: :py:class:`arsenic.services.Service`
    :param browser: The browser to start.
    :type browser: :py:class:`arsenic.browsers.Browser`
    :param str bind: Optional URL to bind the br
    :return: An object which can be passed to :py:func:`stop_session` to stop the session.


.. py:function:: stop_session(session):

    Coroutine to stop a session.

    :param session: The session to stop.
    :type session: Object returned from :py:func:`start_session`.
    :return: Nothing.


All APIs
********

.. toctree::
    :maxdepth: 2

    services
    browsers
    session
    keys
    actions
    errors
    webdriver
    connection
    http
    utils

