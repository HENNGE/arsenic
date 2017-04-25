from aiohttp import web

from arsenic import drivers
from arsenic.clients.aiohttp import AiohttpClient

import pytest

pytestmark = pytest.mark.asyncio()

# Simple Aiohttp app
async def index(request):
    return web.Response(text='Hello Aiohttp!', content_type='text/plain')


def build_app():
    app = web.Application()
    app.router.add_get('/', index)
    return app


async def test_get_page_source(event_loop):
    app = build_app()
    handler = app.make_handler()
    server = await event_loop.create_server(handler, '127.0.0.1', 0)
    port = server.sockets[0].getsockname()[1]
    try:
        async with drivers.context(drivers.FirefoxDriver, AiohttpClient) as driver:
            await driver.get(f'http://127.0.0.1:{port}/')
            assert 'Hello Aiohttp!' in await driver.get_page_source()
    finally:
        server.close()
        await server.wait_closed()
        await app.shutdown()
        await handler.shutdown(10)
        await app.cleanup()
