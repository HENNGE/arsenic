import abc
import asyncio
import re
from distutils.version import StrictVersion
from functools import partial
from typing import List, TextIO, Optional

import attr
import sys
from aiohttp import ClientSession, ClientResponse

from arsenic.connection import Connection, RemoteConnection
from arsenic.subprocess import get_subprocess_impl
from arsenic.utils import free_port
from arsenic.webdriver import WebDriver
from arsenic.http import Auth, BasicAuth


async def tasked(coro):
    return await asyncio.get_event_loop().create_task(coro)


async def check_service_status(session: ClientSession, url: str) -> bool:
    async with session.get(url + "/status") as response:
        return 200 <= response.status < 300


async def subprocess_based_service(
    cmd: List[str], service_url: str, log_file: TextIO
) -> WebDriver:
    closers = []
    try:
        impl = get_subprocess_impl()
        process = await impl.start_process(cmd, log_file)
        closers.append(partial(impl.stop_process, process))
        session = ClientSession()
        closers.append(session.close)
        count = 0
        while True:
            try:
                if await tasked(check_service_status(session, service_url)):
                    break
            except:
                # TODO: make this better
                count += 1
                if count > 30:
                    raise Exception("not starting?")
                await asyncio.sleep(0.5)
        return WebDriver(Connection(session, service_url), closers)
    except:
        for closer in reversed(closers):
            await closer()
        raise


class Service(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def start(self) -> WebDriver:
        raise NotImplementedError()


@attr.s
class Geckodriver(Service):
    log_file = attr.ib(default=sys.stdout)
    binary = attr.ib(default="geckodriver")
    version_check = attr.ib(default=True)

    _version_re = re.compile(r"geckodriver (\d+\.\d+)")

    async def _check_version(self):
        if self.version_check:
            impl = get_subprocess_impl()
            output = await impl.run_process([self.binary, "--version"])
            match = self._version_re.search(output)
            if not match:
                raise ValueError(
                    "Could not determine version of geckodriver. To "
                    "disable version checking, set `version_check` to "
                    "`False`."
                )
            version_str = match.group(1)
            version = StrictVersion(version_str)
            if version < StrictVersion("0.16.1"):
                raise ValueError(
                    f"Geckodriver version {version_str} is too old. 0.16.1 or "
                    f"higher is required. To disable version checking, set "
                    f"`version_check` to `False`."
                )

    async def start(self):
        port = free_port()
        await self._check_version()
        return await subprocess_based_service(
            [self.binary, "--port", str(port)],
            f"http://localhost:{port}",
            self.log_file,
        )


@attr.s
class Chromedriver(Service):
    log_file = attr.ib(default=sys.stdout)
    binary = attr.ib(default="chromedriver")

    async def start(self):
        port = free_port()
        return await subprocess_based_service(
            [self.binary, f"--port={port}"], f"http://localhost:{port}", self.log_file
        )


def auth_or_string(value):
    if value is None:
        return value
    elif isinstance(value, Auth):
        return value
    elif isinstance(value, str) and value.count(":") == 1:
        username, password = value.split(":")
        return BasicAuth(username, password)
    else:
        raise TypeError()


@attr.s
class Remote(Service):
    url: str = attr.ib()
    auth: Optional[Auth] = attr.ib(
        default=None, converter=attr.converters.optional(auth_or_string)
    )

    async def start(self):
        closers = []
        headers = {}
        if self.auth:
            headers.update(self.auth.get_headers())
        try:
            session = ClientSession(headers=headers)
            closers.append(session.close)
            return WebDriver(RemoteConnection(session, self.url), closers)
        except:
            for closer in reversed(closers):
                await closer()
            raise


@attr.s
class PhantomJS(Service):
    log_file = attr.ib(default=sys.stdout)
    binary = attr.ib(default="phantomjs")

    async def start(self):
        port = free_port()
        return await subprocess_based_service(
            [self.binary, f"--webdriver={port}"],
            f"http://localhost:{port}/wd/hub",
            self.log_file,
        )


@attr.s
class IEDriverServer(Service):
    log_file = attr.ib(default=sys.stdout)
    binary = attr.ib(default="IEDriverServer.exe")
    log_level = attr.ib(default="FATAL")

    async def start(self):
        port = free_port()
        return await subprocess_based_service(
            [self.binary, f"/port={port}", f"/log-level={self.log_level}"],
            f"http://localhost:{port}",
            self.log_file,
        )
