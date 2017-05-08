import abc
import os

import attr

from arsenic.connection import Connection
from arsenic.engines import Request
from arsenic.utils import free_port
from arsenic.webdriver import WebDriver


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

    async def start(self, engine):
        port = str(free_port())
        closers = []
        try:
            process = await engine.start_process(
                ['geckodriver', '--port', port],
                os.environ,
                self.log_file
            )
            closers.append(process.close)
            service_url = f'http://localhost:{port}'
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
            return WebDriver(engine, Connection(session, service_url), closers)
        except:
            for closer in reversed(closers):
                await closer()
            raise


@attr.s
class Remote(Service):
    url = attr.ib()
    auth = attr.ib(default=None)

    async def start(self, engine):
        closers = []
        try:
            session = await engine.http_session(self.auth)
            closers.append(session.close)
            return WebDriver(engine, Connection(session, self.url), closers)
        except:
            for closer in reversed(closers):
                await closer()
            raise
