``arsenic.webdriver``
#####################


.. py:module:: arsenic.webdriver


.. py:class:: WebDriver

    Class representing a webdriver. You should not create instances of this
    class yourself, instead let :py:func:`arsenic.get_session` or
    :py:func:`arsenic.start_session` create and manage one for you.

    .. py:method:: wait(timeout, func, *exceptions)

        Coroutine which waits for up to ``timeout`` seconds for the coroutine
        function ``func`` to return a truthy value, calling it repeatedly.

        If the coroutine function ``func`` raises an exception given in
        ``exceptions``, it is ignored.

        If ``func`` returns a truthy value, it is returned to the caller of this
        method.

        :param int timeout: Timeout in seconds.
        :param func: Callback which checks if the condition is met.
        :type func: Coroutine function taking no arguments and returning a truthy value if the condition is met.
        :param Exception exceptions: Optional exceptions to ignore.
