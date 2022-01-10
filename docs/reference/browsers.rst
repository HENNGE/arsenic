``arsenic.browsers``
####################

.. py:module:: arsenic.browsers

.. py:class:: Browser

    Base browser class.

    .. py:attribute:: session_class

        Session class to use for this browser. Should be :py:class:`arsenic.session.Session`
        or a subclass thereof.

    .. py:attribute:: capabilities

        A JSON serializable dictionary of capabilities to request.

    .. py:attribute:: defaults

        Default capabilities.

    .. py:method:: __init__(**overrides):

        When initializing a browser, you can override or extend the default
        capabilities of the browser.


.. py:class:: Firefox(Browser)

    Firefox with default capabilities.


.. py:class:: Chrome(Browser)

    Chrome with default capabilities.


.. py:class:: InternetExplorer(Browser)

    Internet Explorer with default capabilities.
