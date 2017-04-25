from typing import Type

from ..clients import Client
from .remote import RemoteDriver
from .chrome import ChromeDriver
from .firefox import FirefoxDriver


async def init(driver_class: Type[RemoteDriver], client: Client, **kwargs) -> RemoteDriver:
    return await driver_class.async_init(client, **kwargs)


class DriverContext:
    def __init__(self, driver_class: Type[RemoteDriver], client: Client, kwargs):
        self.driver_class = driver_class
        self.client = client
        self.kwargs = kwargs
        self.driver = None

    async def __aenter__(self):
        self.driver = await init(self.driver_class, self.client, **self.kwargs)
        return self.driver

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.driver.quit()


def context(driver_class: Type[RemoteDriver], client: Client, **kwargs) -> DriverContext:
    return DriverContext(driver_class, client, kwargs)
