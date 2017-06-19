``arsenic.connection``
######################

.. py:module:: arsenic.connection


.. py:data:: WEB_ELEMENT

    Constant string used to denote web elements in the web driver protocol.


.. py:class:: Connection(session, prefix)

    Connection class to use for communication with a webdriver. This class
    operates with a ``prefix`` to make it easier to use internally.

    :param session: Aiohttp client session.
    :type session: :py:class:`aiohttp.client.ClientSession`
    :param str prefix: Prefix for this connection.

    .. py:method:: request(*, url, method, data=None, raw=False)

        Coroutine to do an HTTP request. All arguments are keyword only.

        :param str url: The URL to send the request to.
        :param str method: HTTP method to use.
        :param data: Optional data to send. Must be JSON serializable.
        :param bool raw: Optional flag to get the raw response data instead of unwrapped data.

    .. py:method:: upload_file(path):

        Coroutine that uploads a file. This is used for remote webdrivers.
        This is used internally by :py:meth:`arsenic.session.Element.send_file`.

        This method is no-op by default.

        :param path: The (local) path of the file to upload.
        :type path: :py:class:`pathlib.Path`
        :returns: A path indicating the remote path.
        :rtype: :py:class:`pathlib.Path`

    .. py:method:: prefixed(prefix):

        Returns a new connection, inheriting the HTTP session, with the extra
        prefix given.

        :param str prefix: Prefix to add to the current prefix.
        :rtype: :py:class:`Connection`


.. py:class:: RemoteConnection

    Connection class for remote webdrivers. Most notably, :py:meth:`Connection.upload_file`
    is no longer a no-op operation.
