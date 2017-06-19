``arsenic.http``
################

This module holds http authentication helpers.

.. py:module:: arsenic.http

.. py:class:: Auth

    Abstract base class for authentication.

    .. py:method:: get_headers

        Abstract method which returns a dictionary of headers.


.. py:class:: BasicAuth(username, password)

    Basic auth implementation of the :py:class:`Auth` abstract class.
