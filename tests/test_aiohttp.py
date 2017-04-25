from aiohttp import web

from arsenic import drivers
from arsenic.clients.aiohttp import AiohttpClient

import pytest

from .utils import read

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


async def index(request):
    return web.Response(text='Hello Aiohttp!', content_type='text/plain')


async def html(request):
    return web.Response(text=read('simple.html'), content_type='text/html')


async def form(request):
    data = await request.post()
    return web.Response(text=data['field'], content_type='text/plain')


def build_app():
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/html/', html)
    app.router.add_post('/form/', form)
    return app


async def test_get_page_source(app_port):
    async with drivers.context(drivers.FirefoxDriver, AiohttpClient) as driver:
        await driver.get(f'http://127.0.0.1:{app_port}/')
        assert 'Hello Aiohttp!' in await driver.get_page_source()


async def test_simple_form_submit(app_port):
    async with drivers.context(drivers.FirefoxDriver, AiohttpClient) as driver:
        await driver.get(f'http://127.0.0.1:{app_port}/html/')
        field = await driver.find_element_by_css_selector('input[name="field"]')
        await field.send_keys('sample input')
        submit = await driver.find_element_by_css_selector('input[type="submit"]')
        await submit.click()
        assert 'sample input' in await driver.get_page_source()
