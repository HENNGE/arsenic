import pytest

from arsenic.engines.aiohttp import Aiohttp
from tests.aiohttp_app import build_app

pytestmark = pytest.mark.asyncio()


@pytest.fixture(scope='function')
async def app_port(event_loop):
    app = build_app()
    handler = app.make_handler()
    server = await event_loop.create_server(handler, '127.0.0.1', 0)
    port = server.sockets[0].getsockname()[1]
    try:
        yield port
    finally:
        server.close()
        await server.wait_closed()
        await app.shutdown()
        await handler.shutdown(10)
        await app.cleanup()


async def test_get_page_source(app_port, service):
    async with service.driver.run(Aiohttp) as driver:
        async with driver.session(service.browser) as session:
            await session.get(f'http://127.0.0.1:{app_port}/')
            assert 'Hello Aiohttp!' in await session.get_page_source()


async def test_simple_form_submit(app_port, service):
    async with service.driver.run(Aiohttp) as driver:
        async with driver.session(service.browser) as session:
            await session.get(f'http://127.0.0.1:{app_port}/html/')
            field = await session.get_element('input[name="field"]')
            await field.send_keys('sample input')
            submit = await session.get_element('input[type="submit"]')
            await submit.click()
            assert 'sample input' in await session.get_page_source()
