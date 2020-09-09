import asyncio
from typing import Awaitable, Callable, List, Any, Union, Type

import time

from arsenic.browsers import Browser
from arsenic.connection import Connection
from arsenic.errors import ArsenicError, ArsenicTimeout, SessionStartError
from arsenic.session import Session


class SessionContext:
    def __init__(self, driver: "WebDriver", browser: Browser, bind: str):
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
    def __init__(self, connection: Connection, closers: TClosers):
        self.connection = connection
        self.closers = closers

    def session(self, browser: Browser, bind="") -> SessionContext:
        return SessionContext(self, browser, bind)

    async def new_session(self, browser: Browser, bind="") -> Session:
        status, response = await self.connection.request(
            url="/session",
            method="POST",
            data={"capabilities": {"alwaysMatch": browser.capabilities}},
        )
        original_response = response
        if "sessionId" not in response:
            response = response["value"]
        if "sessionId" not in response:
            if "error" in original_response:
                err_resp = original_response
            elif "error" in response:
                err_resp = response
            else:
                raise SessionStartError("Unknown", "Unknown", original_response)
            raise SessionStartError(
                err_resp["error"], err_resp.get("message", ""), original_response
            )
        session_id = response["sessionId"]
        return browser.session_class(
            connection=self.connection.prefixed(f"/session/{session_id}"),
            bind=bind,
            wait=self.wait,
            driver=self,
            browser=browser,
        )

    async def close(self):
        for closer in reversed(self.closers):
            await closer()

    async def wait(
        self,
        timeout: Union[float, int],
        func: Callable[[], Awaitable[Any]],
        *exceptions: Exception,
    ) -> Any:
        deadline = time.time() + timeout
        err = None
        while deadline > time.time():
            try:
                result = await func()
                if result:
                    return result
                else:
                    await asyncio.sleep(0.2)
            except exceptions as exc:
                err = exc
                await asyncio.sleep(0.2)
        raise ArsenicTimeout() from err
