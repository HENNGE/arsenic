from functools import partial
from typing import Awaitable, Callable, List, Any, Sequence, Optional, Union

import time

from arsenic.browsers import Browser
from arsenic.connection import Connection
from arsenic.engines import Engine
from arsenic.errors import ArsenicError, ArsenicTimeout, NoSuchElement

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
        return Element(self.connection.prefixed(f'/element/{element_id}'))

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

    async def close(self):
        await self.connection.request(
            url='',
            method='DELETE'
        )


class SessionContext:
    def __init__(self, driver: 'WebDriver', browser: Browser, bind: str):
        self.driver = driver
        self.browser = browser
        self.bind = bind
        self.session: Session = None

    async def __aenter__(self) -> Session:
        self.session = await self.driver.new_session(self.browser, self.bind)
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        self.session = None


TClosers = List[Callable[..., Awaitable[None]]]


class WebDriver:
    def __init__(self, engine: Engine, connection: Connection, closers: TClosers):
        self.engine = engine
        self.connection = connection
        self.closers = closers

    def session(self, browser: Browser, bind='') -> SessionContext:
        return SessionContext(self, browser, bind)

    async def new_session(self, browser: Browser, bind='') -> Session:
        response = await self.connection.request(
            url='/session',
            method='POST',
            data={
                'desiredCapabilities': browser.capabilities
            },
            raw=True,
        )
        if 'sessionId' not in response:
            response = response['value']
        session_id = response['sessionId']
        return Session(
            connection=self.connection.prefixed(f'/session/{session_id}'),
            bind=bind,
            wait=self.wait,
        )

    async def close(self):
        for closer in reversed(self.closers):
            await closer()

    async def wait(self,
                   timeout: Union[float, int],
                   func: Callable[[], Awaitable[Any]],
                   *exceptions: Exception) -> Any:
        deadline = time.time() + timeout
        err = None
        while deadline > time.time():
            try:
                result = await func()
                if result:
                    return result
                else:
                    await self.engine.sleep(0.2)
            except exceptions as exc:
                err = exc
                await self.engine.sleep(0.2)
        raise ArsenicTimeout() from err
