from functools import partial
from typing import Awaitable, Callable, Any

from arsenic.connection import Connection
from arsenic.errors import NoSuchElement

UNSET = object()


class Element:
    def __init__(self, connection: Connection):
        self.connection = connection

    async def get_text(self):
        return await self.connection.request(
            url='/text',
            method='GET'
        )

    async def send_keys(self, keys):
        await self.connection.request(
            url='/value',
            method='POST',
            data={
                'value': list(keys),
                'text': keys,
            }
        )

    async def click(self):
        await self.connection.request(
            url='/click',
            method='POST'
        )

    async def is_displayed(self):
        return await self.connection.request(
            url='/displayed',
            method='GET'
        )


TCallback = Callable[..., Awaitable[Any]]
TWaiter = Callable[[int, TCallback], Awaitable[Any]]


class Session:
    element_class = Element

    def __init__(self, connection: Connection, wait=TWaiter, bind: str=''):
        self.connection = connection
        self.bind = bind
        self.wait = wait

    async def get(self, url: str):
        await self.connection.request(
            url='/url',
            method='POST',
            data={
                'url': self.bind + url
            }
        )

    async def get_url(self):
        return await self.connection.request(
            url='/url',
            method='GET'
        )

    async def get_page_source(self):
        return await self.connection.request(
            url='/source',
            method='GET'
        )

    async def get_element(self, selector: str) -> Element:
        element_id = await self.connection.request(
            url='/element',
            method='POST',
            data={
                'using': 'css selector',
                'value': selector
            }
        )
        return self.element_class(self.connection.prefixed(f'/element/{element_id}'))

    async def wait_for_element(self, timeout: int, selector: str) -> Element:
        return await self.wait(
            timeout,
            partial(self.get_element, selector),
            NoSuchElement
        )

    async def wait_for_element_gone(self, timeout: int, selector: str):
        async def callback():
            try:
                await self.get_element(selector)
            except NoSuchElement:
                return True
            else:
                return False
        return await self.wait(timeout, callback)

    async def add_cookie(self, name, value, *, path=UNSET, domain=UNSET, secure=UNSET, expiry=UNSET):
        cookie = {
            'name': name,
            'value': value
        }
        if path is not UNSET:
            cookie['path'] = path
        if domain is not UNSET:
            cookie['domain'] = domain
        if secure is not UNSET:
            cookie['secure'] = secure
        if expiry is not UNSET:
            cookie['expiry'] = expiry
        await self.connection.request(
            url='/cookie',
            method='POST',
            data={
                'cookie': cookie
            }
        )

    async def get_cookie(self, name):
        return await self.connection.request(
            url=f'/cookie/{name}',
            method='GET'
        )

    async def get_all_cookies(self):
        return await self.connection.request(
            url='/cookie',
            method='GET'
        )

    async def delete_cookie(self, name):
        await self.connection.request(
            url=f'/cookie/{name}',
            method='DELETE'
        )

    async def delete_all_cookies(self):
        await self.connection.request(
            url='/cookie',
            method='DELETE'
        )

    async def execute_script(self, script, *args):
        return await self.connection.request(
            url='/execute/sync',
            method='POST',
            data={
                'script': script,
                'args': list(args)
            }
        )

    async def set_window_size(self, width: int, height: int, handle: str='current'):
        return await self.connection.request(
            url='/window/rect',
            method='POST',
            data={
                'width': width,
                'height': height,
                'windowHandle': handle,
            }
        )

    async def get_window_size(self, handle: str='current'):
        return await self.connection.request(
            url='/window/rect',
            method='GET',
            data={
                'windowHandle': handle,
            }
        )

    async def close(self):
        await self.connection.request(
            url='',
            method='DELETE'
        )


class CompatSession(Session):
    async def set_window_size(self, width: int, height: int,
                              handle: str = 'current'):
        return await self.connection.request(
            url=f'/window/{handle}/size',
            method='POST',
            data={
                'width': width,
                'height': height
            }
        )

    async def get_window_size(self, handle: str = 'current'):
        return await self.connection.request(
            url=f'/window/{handle}/size',
            method='GET'
        )

    async def execute_script(self, script, *args):
        return await self.connection.request(
            url='/execute',
            method='POST',
            data={
                'script': script,
                'args': list(args)
            }
        )

