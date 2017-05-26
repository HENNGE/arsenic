import abc
import os
from typing import List, TextIO

import attr

from arsenic.connection import Connection, RemoteConnection
from arsenic.engines import Request, Engine, Auth, BasicAuth
from arsenic.utils import free_port
from arsenic.webdriver import WebDriver


async def subprocess_based_service(engine: Engine,
                                   cmd: List[str],
                                   service_url: str,
                                   log_file: TextIO) -> WebDriver:
    closers = []
    try:
        process = await engine.start_process(
            cmd,
            os.environ,
            log_file
        )
        closers.append(process.close)
        session = await engine.http_session()
        closers.append(session.close)
        request = Request(
            url=service_url + '/status',
            method='GET'
        )
        count = 0
        while True:
            try:
                await session.request(request)
                break
            except:
                count += 1
                if count > 30:
                    raise Exception('not starting?')
                await engine.sleep(0.5)
        return WebDriver(
            engine,
            Connection(session, service_url),
            closers,
        )
    except:
        for closer in reversed(closers):
            await closer()
        raise


class Service(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def start(self, engine):
        raise NotImplementedError()

    def run(self, engine):
        return ServiceContext(self, engine)


@attr.s
class ServiceContext:
    service: Service = attr.ib()
    engine = attr.ib()
    driver = attr.ib(default=None)

    async def __aenter__(self):
        self.driver = await self.service.start(self.engine)
        return self.driver

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.driver.close()
        self.driver = None


@attr.s
class Geckodriver(Service):
    log_file = attr.ib(default=os.devnull)
    binary = attr.ib(default='geckodriver')

    async def start(self, engine):
        port = free_port()
        return await subprocess_based_service(
            engine,
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
    url = attr.ib()
    auth = attr.ib(default=None, convert=attr.converters.optional(auth_or_string))

    async def start(self, engine):
        closers = []
        try:
            session = await engine.http_session(self.auth)
            closers.append(session.close)
            return WebDriver(engine, RemoteConnection(session, self.url), closers)
        except:
            for closer in reversed(closers):
                await closer()
            raise


@attr.s
class PhantomJS(Service):
    log_file = attr.ib(default=os.devnull)
    binary = attr.ib(default='phantomjs')

    async def start(self, engine):
        port = free_port()
        return await subprocess_based_service(
            engine,
            [self.binary, f'--webdriver={port}'],
            f'http://localhost:{port}/wd/hub',
            self.log_file,
        )
