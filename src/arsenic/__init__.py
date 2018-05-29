import attr

from arsenic.browsers import Browser
from arsenic.services import Service
from arsenic.session import Session


@attr.s
class SessionContext:
    service = attr.ib()
    browser = attr.ib()
    bind = attr.ib()
    session = attr.ib(default=None)

    async def __aenter__(self):
        self.session = await start_session(self.service, self.browser, self.bind)
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await stop_session(self.session)


def get_session(service, browser, bind=""):
    return SessionContext(service, browser, bind)


async def start_session(service: Service, browser: Browser, bind=""):
    driver = await service.start()
    return await driver.new_session(browser, bind=bind)


async def stop_session(session: Session):
    await session.close()
    await session.driver.close()
