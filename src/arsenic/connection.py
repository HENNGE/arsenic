# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import logging
import string
import base64
from urllib.parse import urlparse

from selenium.webdriver.remote import utils
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.errorhandler import ErrorCode

from arsenic.clients import Client, Request, Response

LOGGER = logging.getLogger(__name__)


def get_headers(parsed_url):
    """
    Get headers for remote request.

    :Args:
     - parsed_url - The parsed url
     - keep_alive (Boolean) - Is this a keep-alive connection (default: False)
    """

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': 'Arsenic'
    }

    if parsed_url.username:
        base64string = base64.b64encode(
            f'{parsed_url.username}:{parsed_url.password}'.encode()
        )
        headers.update({
            'Authorization': 'Basic {}'.format(base64string.decode())
        })

    return headers


class RemoteConnection:
    def __init__(self, client: Client, *, remote_server_addr):
        # Attempt to resolve the hostname and get an IP address.
        self._client = client
        self._url = remote_server_addr
        self._session = None

        self._commands = {
            Command.STATUS: ('GET', '/status'),
            Command.NEW_SESSION: ('POST', '/session'),
            Command.GET_ALL_SESSIONS: ('GET', '/sessions'),
            Command.QUIT: ('DELETE', '/session/$sessionId'),
            Command.GET_CURRENT_WINDOW_HANDLE:
                ('GET', '/session/$sessionId/window_handle'),
            Command.W3C_GET_CURRENT_WINDOW_HANDLE:
                ('GET', '/session/$sessionId/window'),
            Command.GET_WINDOW_HANDLES:
                ('GET', '/session/$sessionId/window_handles'),
            Command.W3C_GET_WINDOW_HANDLES:
                ('GET', '/session/$sessionId/window/handles'),
            Command.GET: ('POST', '/session/$sessionId/url'),
            Command.GO_FORWARD: ('POST', '/session/$sessionId/forward'),
            Command.GO_BACK: ('POST', '/session/$sessionId/back'),
            Command.REFRESH: ('POST', '/session/$sessionId/refresh'),
            Command.EXECUTE_SCRIPT: ('POST', '/session/$sessionId/execute'),
            Command.W3C_EXECUTE_SCRIPT:
                ('POST', '/session/$sessionId/execute/sync'),
            Command.W3C_EXECUTE_SCRIPT_ASYNC:
                ('POST', '/session/$sessionId/execute/async'),
            Command.GET_CURRENT_URL: ('GET', '/session/$sessionId/url'),
            Command.GET_TITLE: ('GET', '/session/$sessionId/title'),
            Command.GET_PAGE_SOURCE: ('GET', '/session/$sessionId/source'),
            Command.SCREENSHOT: ('GET', '/session/$sessionId/screenshot'),
            Command.ELEMENT_SCREENSHOT: ('GET', '/session/$sessionId/element/$id/screenshot'),
            Command.FIND_ELEMENT: ('POST', '/session/$sessionId/element'),
            Command.FIND_ELEMENTS: ('POST', '/session/$sessionId/elements'),
            Command.W3C_GET_ACTIVE_ELEMENT: ('GET', '/session/$sessionId/element/active'),
            Command.GET_ACTIVE_ELEMENT:
                ('POST', '/session/$sessionId/element/active'),
            Command.FIND_CHILD_ELEMENT:
                ('POST', '/session/$sessionId/element/$id/element'),
            Command.FIND_CHILD_ELEMENTS:
                ('POST', '/session/$sessionId/element/$id/elements'),
            Command.CLICK_ELEMENT: ('POST', '/session/$sessionId/element/$id/click'),
            Command.CLEAR_ELEMENT: ('POST', '/session/$sessionId/element/$id/clear'),
            Command.SUBMIT_ELEMENT: ('POST', '/session/$sessionId/element/$id/submit'),
            Command.GET_ELEMENT_TEXT: ('GET', '/session/$sessionId/element/$id/text'),
            Command.SEND_KEYS_TO_ELEMENT:
                ('POST', '/session/$sessionId/element/$id/value'),
            Command.SEND_KEYS_TO_ACTIVE_ELEMENT:
                ('POST', '/session/$sessionId/keys'),
            Command.UPLOAD_FILE: ('POST', "/session/$sessionId/file"),
            Command.GET_ELEMENT_VALUE:
                ('GET', '/session/$sessionId/element/$id/value'),
            Command.GET_ELEMENT_TAG_NAME:
                ('GET', '/session/$sessionId/element/$id/name'),
            Command.IS_ELEMENT_SELECTED:
                ('GET', '/session/$sessionId/element/$id/selected'),
            Command.SET_ELEMENT_SELECTED:
                ('POST', '/session/$sessionId/element/$id/selected'),
            Command.IS_ELEMENT_ENABLED:
                ('GET', '/session/$sessionId/element/$id/enabled'),
            Command.IS_ELEMENT_DISPLAYED:
                ('GET', '/session/$sessionId/element/$id/displayed'),
            Command.GET_ELEMENT_LOCATION:
                ('GET', '/session/$sessionId/element/$id/location'),
            Command.GET_ELEMENT_LOCATION_ONCE_SCROLLED_INTO_VIEW:
                ('GET', '/session/$sessionId/element/$id/location_in_view'),
            Command.GET_ELEMENT_SIZE:
                ('GET', '/session/$sessionId/element/$id/size'),
            Command.GET_ELEMENT_RECT:
                ('GET', '/session/$sessionId/element/$id/rect'),
            Command.GET_ELEMENT_ATTRIBUTE:
                ('GET', '/session/$sessionId/element/$id/attribute/$name'),
            Command.GET_ELEMENT_PROPERTY:
                ('GET', '/session/$sessionId/element/$id/property/$name'),
            Command.ELEMENT_EQUALS:
                ('GET', '/session/$sessionId/element/$id/equals/$other'),
            Command.GET_ALL_COOKIES: ('GET', '/session/$sessionId/cookie'),
            Command.ADD_COOKIE: ('POST', '/session/$sessionId/cookie'),
            Command.DELETE_ALL_COOKIES:
                ('DELETE', '/session/$sessionId/cookie'),
            Command.DELETE_COOKIE:
                ('DELETE', '/session/$sessionId/cookie/$name'),
            Command.SWITCH_TO_FRAME: ('POST', '/session/$sessionId/frame'),
            Command.SWITCH_TO_PARENT_FRAME: ('POST', '/session/$sessionId/frame/parent'),
            Command.SWITCH_TO_WINDOW: ('POST', '/session/$sessionId/window'),
            Command.CLOSE: ('DELETE', '/session/$sessionId/window'),
            Command.GET_ELEMENT_VALUE_OF_CSS_PROPERTY:
                ('GET', '/session/$sessionId/element/$id/css/$propertyName'),
            Command.IMPLICIT_WAIT:
                ('POST', '/session/$sessionId/timeouts/implicit_wait'),
            Command.EXECUTE_ASYNC_SCRIPT: ('POST', '/session/$sessionId/execute_async'),
            Command.SET_SCRIPT_TIMEOUT:
                ('POST', '/session/$sessionId/timeouts/async_script'),
            Command.SET_TIMEOUTS:
                ('POST', '/session/$sessionId/timeouts'),
            Command.DISMISS_ALERT:
                ('POST', '/session/$sessionId/dismiss_alert'),
            Command.W3C_DISMISS_ALERT:
                ('POST', '/session/$sessionId/alert/dismiss'),
            Command.ACCEPT_ALERT:
                ('POST', '/session/$sessionId/accept_alert'),
            Command.W3C_ACCEPT_ALERT:
                ('POST', '/session/$sessionId/alert/accept'),
            Command.SET_ALERT_VALUE:
                ('POST', '/session/$sessionId/alert_text'),
            Command.W3C_SET_ALERT_VALUE:
                ('POST', '/session/$sessionId/alert/text'),
            Command.GET_ALERT_TEXT:
                ('GET', '/session/$sessionId/alert_text'),
            Command.W3C_GET_ALERT_TEXT:
                ('GET', '/session/$sessionId/alert/text'),
            Command.SET_ALERT_CREDENTIALS:
                ('POST', '/session/$sessionId/alert/credentials'),
            Command.CLICK:
                ('POST', '/session/$sessionId/click'),
            Command.W3C_ACTIONS:
                ('POST', '/session/$sessionId/actions'),
            Command.W3C_CLEAR_ACTIONS:
                ('DELETE', '/session/$sessionId/actions'),
            Command.DOUBLE_CLICK:
                ('POST', '/session/$sessionId/doubleclick'),
            Command.MOUSE_DOWN:
                ('POST', '/session/$sessionId/buttondown'),
            Command.MOUSE_UP:
                ('POST', '/session/$sessionId/buttonup'),
            Command.MOVE_TO:
                ('POST', '/session/$sessionId/moveto'),
            Command.GET_WINDOW_SIZE:
                ('GET', '/session/$sessionId/window/$windowHandle/size'),
            Command.W3C_GET_WINDOW_SIZE:
                ('GET', '/session/$sessionId/window/size'),
            Command.SET_WINDOW_SIZE:
                ('POST', '/session/$sessionId/window/$windowHandle/size'),
            Command.W3C_SET_WINDOW_SIZE:
                ('POST', '/session/$sessionId/window/size'),
            Command.GET_WINDOW_POSITION:
                ('GET', '/session/$sessionId/window/$windowHandle/position'),
            Command.SET_WINDOW_POSITION:
                ('POST', '/session/$sessionId/window/$windowHandle/position'),
            Command.W3C_GET_WINDOW_POSITION:
                ('GET', '/session/$sessionId/window/position'),
            Command.W3C_SET_WINDOW_POSITION:
                ('POST', '/session/$sessionId/window/position'),
            Command.SET_WINDOW_RECT:
                ('POST', '/session/$sessionId/window/rect'),
            Command.GET_WINDOW_RECT:
                ('GET', '/session/$sessionId/window/rect'),
            Command.MAXIMIZE_WINDOW:
                ('POST', '/session/$sessionId/window/$windowHandle/maximize'),
            Command.W3C_MAXIMIZE_WINDOW:
                ('POST', '/session/$sessionId/window/maximize'),
            Command.SET_SCREEN_ORIENTATION:
                ('POST', '/session/$sessionId/orientation'),
            Command.GET_SCREEN_ORIENTATION:
                ('GET', '/session/$sessionId/orientation'),
            Command.SINGLE_TAP:
                ('POST', '/session/$sessionId/touch/click'),
            Command.TOUCH_DOWN:
                ('POST', '/session/$sessionId/touch/down'),
            Command.TOUCH_UP:
                ('POST', '/session/$sessionId/touch/up'),
            Command.TOUCH_MOVE:
                ('POST', '/session/$sessionId/touch/move'),
            Command.TOUCH_SCROLL:
                ('POST', '/session/$sessionId/touch/scroll'),
            Command.DOUBLE_TAP:
                ('POST', '/session/$sessionId/touch/doubleclick'),
            Command.LONG_PRESS:
                ('POST', '/session/$sessionId/touch/longclick'),
            Command.FLICK:
                ('POST', '/session/$sessionId/touch/flick'),
            Command.EXECUTE_SQL:
                ('POST', '/session/$sessionId/execute_sql'),
            Command.GET_LOCATION:
                ('GET', '/session/$sessionId/location'),
            Command.SET_LOCATION:
                ('POST', '/session/$sessionId/location'),
            Command.GET_APP_CACHE:
                ('GET', '/session/$sessionId/application_cache'),
            Command.GET_APP_CACHE_STATUS:
                ('GET', '/session/$sessionId/application_cache/status'),
            Command.CLEAR_APP_CACHE:
                ('DELETE', '/session/$sessionId/application_cache/clear'),
            Command.GET_NETWORK_CONNECTION:
                ('GET', '/session/$sessionId/network_connection'),
            Command.SET_NETWORK_CONNECTION:
                ('POST', '/session/$sessionId/network_connection'),
            Command.GET_LOCAL_STORAGE_ITEM:
                ('GET', '/session/$sessionId/local_storage/key/$key'),
            Command.REMOVE_LOCAL_STORAGE_ITEM:
                ('DELETE', '/session/$sessionId/local_storage/key/$key'),
            Command.GET_LOCAL_STORAGE_KEYS:
                ('GET', '/session/$sessionId/local_storage'),
            Command.SET_LOCAL_STORAGE_ITEM:
                ('POST', '/session/$sessionId/local_storage'),
            Command.CLEAR_LOCAL_STORAGE:
                ('DELETE', '/session/$sessionId/local_storage'),
            Command.GET_LOCAL_STORAGE_SIZE:
                ('GET', '/session/$sessionId/local_storage/size'),
            Command.GET_SESSION_STORAGE_ITEM:
                ('GET', '/session/$sessionId/session_storage/key/$key'),
            Command.REMOVE_SESSION_STORAGE_ITEM:
                ('DELETE', '/session/$sessionId/session_storage/key/$key'),
            Command.GET_SESSION_STORAGE_KEYS:
                ('GET', '/session/$sessionId/session_storage'),
            Command.SET_SESSION_STORAGE_ITEM:
                ('POST', '/session/$sessionId/session_storage'),
            Command.CLEAR_SESSION_STORAGE:
                ('DELETE', '/session/$sessionId/session_storage'),
            Command.GET_SESSION_STORAGE_SIZE:
                ('GET', '/session/$sessionId/session_storage/size'),
            Command.GET_LOG:
                ('POST', '/session/$sessionId/log'),
            Command.GET_AVAILABLE_LOG_TYPES:
                ('GET', '/session/$sessionId/log/types'),
            Command.CURRENT_CONTEXT_HANDLE:
                ('GET', '/session/$sessionId/context'),
            Command.CONTEXT_HANDLES:
                ('GET', '/session/$sessionId/contexts'),
            Command.SWITCH_TO_CONTEXT:
                ('POST', '/session/$sessionId/context'),
        }

    async def initialize(self):
        self._session = await self._client.init_session()

    async def finalize(self):
        await self._client.close_session(self._session)
        self._session = None

    async def execute(self, command, params):
        """
        Send a command to the remote server.

        Any path subtitutions required for the URL mapped to the command should be
        included in the command parameters.

        :Args:
         - command - A string specifying the command to execute.
         - params - A dictionary of named parameters to send with the command as
           its JSON payload.
        """
        command_info = self._commands[command]
        assert command_info is not None, 'Unrecognised command %s' % command
        data = utils.dump_json(params)
        path = string.Template(command_info[1]).substitute(params)
        url = '%s%s' % (self._url, path)
        return await self._request(command_info[0], url, body=data)

    async def _request(self, method, url, body=None):
        """
        Send an HTTP request to the remote server.

        :Args:
         - method - A string for the HTTP method to send the request with.
         - url - A string for the URL to send the request to.
         - body - A string for request body. Ignored unless method is POST or PUT.

        :Returns:
          A dictionary with the server's parsed JSON response.
        """
        LOGGER.debug('%s %s %s' % (method, url, body))

        parsed_url = urlparse(url)
        headers = get_headers(parsed_url)

        if body and method != 'POST' and method != 'PUT':
            body = None
        request = Request(
            method=method,
            url=url,
            headers=headers,
            body=body,
        )
        response: Response = await self._client.send_request(
            self._session,
            request
        )
        try:
            body = response.body.decode('utf-8').replace('\x00', '').strip()
            if 399 < response.status <= 500:
                return {'status': response.status, 'value': body}
            content_type = response.headers.get('Content-Type', None)
            is_image = content_type is not None and any(
                part.startswith('image/png') for part in content_type.split(';')
            )
            if not is_image:
                try:
                    data = utils.load_json(body.strip())
                except ValueError:
                    if 199 < response.status < 300:
                        status = ErrorCode.SUCCESS
                    else:
                        status = ErrorCode.UNKNOWN_ERROR
                    return {'status': status, 'value': body.strip()}

                if not isinstance(data, dict):
                    raise TypeError(f'Invalid server response body: {body}')
                # Some of the drivers incorrectly return a response
                # with no 'value' field when they should return null.
                if 'value' not in data:
                    data['value'] = None
                return data
            else:
                data = {'status': 0, 'value': body.strip()}
                return data
        finally:
            LOGGER.debug("Finished Request")
