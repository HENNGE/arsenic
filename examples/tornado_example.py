import os

from tornado.ioloop import IOLoop

from arsenic.engines import BasicAuth
from arsenic.engines.tornado import Tornado
from arsenic.browsers import Firefox
from arsenic.services import Geckodriver, Remote


async def get_example_h1_context_manager(service, engine):
    async with service.run(engine) as driver:
        async with driver.session(Firefox()) as session:
            await session.get('http://example.com/')
            element = await session.get_element('h1')
            print(await element.get_text())


async def get_example_h1_functional(service, engine):
    driver = await service.start(engine)
    try:
        session = await driver.new_session(Firefox())
        try:
            await session.get('http://example.com/')
            element = await session.get_element('h1')
            print(await element.get_text())
        finally:
            await session.close()
    finally:
        await driver.close()


async def gecko(func):
    await func(
        Geckodriver(),
        Tornado
    )


async def remote(func):
    await func(
        Remote(
            'http://hub.browserstack.com/wd/hub',
            BasicAuth(
                os.environ['USERNAME'],
                os.environ['PASSWORD'],
            )
        ),
        Tornado
    )


async def run():
    await gecko(get_example_h1_context_manager)
    await gecko(get_example_h1_functional)
    await remote(get_example_h1_context_manager)
    await remote(get_example_h1_functional)


def main():
    IOLoop.current().run_sync(run)


if __name__ == '__main__':
    main()
