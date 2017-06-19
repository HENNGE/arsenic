``arsenic.errors``
##################

.. py:exception:: ArsenicError

    Base exception class used by arsenic.

.. py:exception:: OperationNotSupported

    Exception raised for operations not supported by a given webdriver and/or
    browser.

.. py:exception:: WebdriverError

    Base class for webdriver-side errors.


.. py:exception:: UnkownArsenicError

    Exception used when there was a webdriver-side error, but arsenic could not
    figure out what the error was.


.. py:exception:: ArsenicTimeout

    Raised when :py:meth:`arsenic.webdriver.WebDriver.wait`,
    :py:meth:`arsenic.session.Session.wait` or a higher level wait API times out.


The following are specific exceptions which may be returned from a webdriver.
Consult the webdriver specification for details.

.. py:exception:: NoSuchElement
.. py:exception:: NoSuchFrame
.. py:exception:: UnknownCommand
.. py:exception:: StaleElementReference
.. py:exception:: ElementNotVisible
.. py:exception:: InvalidElementState
.. py:exception:: UnknownError
.. py:exception:: ElementNotInteractable
.. py:exception:: ElementIsNotSelectable
.. py:exception:: JavascriptError
.. py:exception:: Timeout
.. py:exception:: NoSuchWindow
.. py:exception:: InvalidCookieDomain
.. py:exception:: UnableToSetCookie
.. py:exception:: UnexpectedAlertOpen
.. py:exception:: NoSuchAlert
.. py:exception:: ScriptTimeout
.. py:exception:: InvalidElementCoordinates
.. py:exception:: IMENotAvailable
.. py:exception:: IMEEngineActivationFailed
.. py:exception:: InvalidSelector
.. py:exception:: MoveTargetOutOfBounds
