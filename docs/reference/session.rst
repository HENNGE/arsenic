``arsenic.session``
###################

.. py:module:: arsenic.session

.. py:class:: Element

    A web element. You should not create instances of this class yourself,
    instead use :py:meth:`Session.get_element` or :py:meth:`Session.get_elements`.

    .. py:method:: get_text()

        Coroutine to get the text of this element.

        :rtype: str

    .. py:method:: send_keys(keys)

        Coroutine to send a sequence of keys to this element. Useful for text inputs.

        :param str keys: The keys to send. Use :py:mod:`arsenic.keys` for special keys.


    .. py:method:: send_file(path):

        Coroutine to send a file to this element. Useful for file inputs.

        :param pathlib.Path path: The local path to the file.

    .. py:method:: clear

        Coroutine to clear this element. Useful for form inputs.

    .. py:method:: click

        Coroutine to click on this element.

    .. py:method:: is_displayed

        Coroutine to check if this element is displayed or not.

        :rtype: bool

    .. py:method:: is_enabled

        Coroutine to check if this element is enabled.

        :rtype: bool

    .. py:method:: get_attribute(name)

        Coroutine which returns the value of a given attribute of this element.

        :param str name: Name of the attribute to get.
        :rtype: str

    .. py:method:: get_property(name)

        Coroutine which returns the value of a given property of this element.

        :param str name: Name of the property to get.
        :rtype: str

    .. py:method:: select_by_value(value)

        Coroutine to select an option by value. This is useful if this element is a select
        input.

        :param str value: Value of the option to select.

    .. py:method:: get_rect()

        Coroutine to get the location and size of the element.

        :rtype: :py:class:`arsenic.utils.Rect`

    .. py:method:: get_element(selector)

        Coroutine to get a child element of this element via CSS selector.

        :param str selector: CSS selector.
        :rtype: :py:class:`Element`

    .. py:method:: get_elements(selector)

        Coroutine to get a list of child elements of this element via CSS selector.

        :param str selector: CSS selector.
        :rtype: List of :py:class:`Element` instances.


.. py:class:: Session

    A webdriver session. You should not create instances of this class yourself,
    instead use :py:func:`arsenic.get_session` or :py:func:`arsenic.start_session`.

   .. py:method:: request(url, method='GET', data=UNSET):

        Coroutine to perform a direct webdriver request.

        :param str url: URL to call.
        :param str method: method to use
        :param Dict[str, Any]: data to send

   .. py:method:: get(url):

        Coroutine to navigate to a given url.

        :param str url: URL to navigate to.

    .. py:method:: get_url

        Coroutine to get the current URL.

        :rtype: str

    .. py:method:: get_page_source

        Coroutine to get the source of the current page.

        :rtype: str

    .. py:method:: get_element(selector)

        Coroutine to get an element via CSS selector.

        :param str selector: CSS selector of the element.
        :rtype: :py:class:`Element`

    .. py:method:: get_elements(selector)

        Coroutine to get a list of elements via CSS selector.

        :param str selector: CSS selector of the elements.
        :rtype: List of :py:class:`Element` instances.

    .. py:method:: wait_for_element(timeout, selector)

        Coroutine like :py:meth:`get_element`, but waits up to ``timeout`` seconds
        for the element to appear.

        :param int timeout: Timeout in seconds.
        :param str selector: CSS selector.
        :rtype: :py:class:`Element`

    .. py:method:: wait_for_element_gone(timeout, selector)

        Coroutine that waits up to ``timeout`` seconds for the element for the
        given CSS selector to no longer be available.

        :param int timeout: Timeout in seconds.
        :param str selector: CSS Selector.
        :rtype: None

    .. py:method:: add_cookie(name, value, *, path=UNSET, domain=UNSET, secure=UNSET, expiry=UNSET)

        Coroutine to set a cookie.

        :param str name: Name of the cookie.
        :param str value: Value of the cookie.
        :param str path: Optional, keyword-only path of the cookie.
        :param str domain: Optional, keyword-only domain of the cookie.
        :param bool secure: Optional, keyword-only secure flag of the cookie.
        :param int expiry: Optional, keyword-only expiration of the cookie.
        :param bool httponly: Optional, keyword-only httponly flag of the cookie.
        :rtype: None

    .. py:method:: get_cookie(name)

        Coroutine to get the value of a cookie.

        :param str name: Name of the cookie.
        :rtype: str

    .. py:method:: get_all_cookies

        Coroutine to get all cookies.

        :rtype: dict

    .. py:method:: delete_cookie(name)

        Coroutine to delete a specific cookie.

        :param str name: Name of the cookie to delete.

    .. py:method:: delete_all_cookies

        Coroutine to delete all cookies.

    .. py:method:: execute_script(script, *args)

        Coroutine which executes a javascript script with the given arguments.

        :param str script: Javascript script source to execute.
        :param args: Arguments to pass to the script. Must be JSON serializable.

    .. py:method:: set_window_size(width, height, handle='current')

        Coroutine to set the size of a given window.

        :param int width: Width in pixels.
        :param int height: Height in pixels.
        :param str handle: ID of the window.

    .. py:method:: get_window_size(handle='current')

        Coroutine to get the size of a given window.

        :param str handle: ID of the window.
        :rtype: Tuple[int, int]

    .. py:method:: get_window_handle()

        Coroutine to get the handle of the current window

        :rtype: str

    .. py:method:: switch_to_window(handle)

        Coroutine to set the handle of the current window

        :param str handle: ID of the window.
        :rtype: str

    .. py:method:: get_window_handles()

        Coroutine to get the handles of all windows

        :rtype: List[str]

    .. py:method:: new_window(window_type=WindowType.tab.value)

        Coroutine to open new window

        :param str window_type: type of the window to open: value can be "window" or "tab"
        :rtype: dict, containing window handle and window type, example: {"handle": "17", "type": "tab"}

    .. py:method:: get_alert_text

        Coroutine to return the text of an alert message.

        :rtype: str

    .. py:method:: send_alert_text(value)

        Coroutine to send text to an alert message.

        :param str value: Value to send.

    .. py:method:: dismiss_alert

        Coroutine to dismiss an active alert.

    .. py:method:: accept_alert

        Coroutine to accept an active alert.

    .. py:method:: perform_actions(actions)

        Coroutine to perform a series of actions. Use :py:func:`arsenic.actions.chain`
        to build the actions object.

    .. py:method:: get_screenshot

        Coroutine to take a screenshot of the top-level browsing context’s viewport.

        :rtype: :py:class:`io.BytesIO`

    .. py:method:: close

        Coroutine to close this session.
