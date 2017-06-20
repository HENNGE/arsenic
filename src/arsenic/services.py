import abc
import asyncio
import os
from asyncio.subprocess import DEVNULL
from functools import partial
from typing import List, TextIO, Optional

import attr
from aiohttp import ClientSession

from arsenic.connection import Connection, RemoteConnection
from arsenic.utils import free_port
from arsenic.webdriver import WebDriver
from arsenic.http import Auth, BasicAuth


async def stop_process(process):
    process.terminate()
    try:
        await asyncio.wait_for(process.communicate(), 1)
    except asyncio.futures.TimeoutError:
        process.kill()
    try:
        await asyncio.wait_for(process.communicate(), 1)
    except asyncio.futures.TimeoutError:
        pass


def sync_factory(func):
    async def sync():
        func()
    return sync


async def tasked(coro):
    return await asyncio.get_event_loop().create_task(coro)


async def subprocess_based_service(cmd: List[str],
                                   service_url: str,
                                   log_file: TextIO) -> WebDriver:
    closers = []
    try:
        if log_file is os.devnull:
            log_file = DEVNULL
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=log_file,
            stderr=log_file,
        )
        closers.append(partial(stop_process, process))
        session = ClientSession()
        closers.append(sync_factory(session.close))
        count = 0
        while True:
            try:
                await tasked(session.request(
                    url=service_url + '/status',
                    method='GET'
                ))
                break
            except:
                # TODO: make this better
                count += 1
                if count > 30:
                    raise Exception('not starting?')
                await asyncio.sleep(0.5)
        return WebDriver(
            Connection(session, service_url),
            closers,
        )
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
    log_file = attr.ib(default=os.devnull)
    binary = attr.ib(default='geckodriver')

    async def start(self):
        port = free_port()
        return await subprocess_based_service(
            [self.binary, '--port', str(port)],
            f'http://localhost:{port}',
            self.log_file
        )


def auth_or_string(value):
    if isinstance(value, Auth):
        return value
    elif isinstance(value, str) and value.count(':') == 1:
        username, password = value.split(':')
        return BasicAuth(username, password)
    else:
        raise TypeError()


@attr.s
class Remote(Service):
    url: str = attr.ib()
    auth: Optional[Auth] = attr.ib(default=None, convert=attr.converters.optional(auth_or_string))

    async def start(self):
        closers = []
        headers = {}
        if self.auth:
            headers.update(self.auth.get_headers())
        try:
            session = ClientSession(headers=headers)
            closers.append(sync_factory(session.close))
            return WebDriver(RemoteConnection(session, self.url), closers)
        except:
            for closer in reversed(closers):
                await closer()
            raise


@attr.s
class PhantomJS(Service):
    log_file = attr.ib(default=os.devnull)
    binary = attr.ib(default='phantomjs')

    async def start(self):
        port = free_port()
        return await subprocess_based_service(
            [self.binary, f'--webdriver={port}'],
            f'http://localhost:{port}/wd/hub',
            self.log_file,
        )
