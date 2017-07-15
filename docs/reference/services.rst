``arsenic.services``
####################

.. py:module:: arsenic.services

.. py:function:: stop_process(process)

    Coroutine that stops a process.

    :param process: Process to stop
    :type process: :py:class:`asyncio.subprocess.Process`


.. py:function:: sync_factory(func)

    Factory function which returns a coroutine which calls the function passed
    in. Useful to wrap a non-coroutine function as a coroutine for APIs that
    require coroutines.


.. py:function:: subprocess_baed_service(cmd, service_url, log_file)

    Helper function for services that run a local subprocess.

    :param List[str] cmd: Command to run.
    :param str service_url: URL at which the service will be available after starting.
    :param io.TextIO log_file: Log file for the service.
    :rtype: :py:class:`arsenic.webdriver.WebDriver`


.. py:class:: Service

    Abstract base class for services.

    .. py:method:: start

        Abstract method to start a service.

        :rtype: :py:class:`arsenic.webdriver.WebDriver`


.. py:class:: Geckodriver(log_file=os.devnull, binary='geckodriver')

    Geckodriver service. Requires geckodriver 0.17 or higher.

    :param io.TextIO log_file: Log file to use.
    :param str binary: Path to the geckodriver binary.
    :param bool version_check: Optional flag to disable version checking.


.. py:class:: Remote(url, auth=None)

    Remote service.

    :param str url: URL of the remote webdriver.
    :param auth: Optional authentication.
    :type auth: :py:class:`arsenic.http.Auth` or :py:class:`str`.



.. py:class:: PhantomJS(log_file=os.devnull, binary='phantomjs')

    PhantomJS service.

    :param io.TextIO log_file: Log file to use.
    :param str binary: Path to the PhantomJS binary.
