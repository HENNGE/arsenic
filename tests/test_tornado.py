import pytest
from tornado.httpserver import HTTPServer
from tornado.web import RequestHandler, Application

from arsenic import drivers
from arsenic.clients.tornado import TornadoClient


pytestmark = pytest.mark.gen_test(timeout=60)


# Simple Tornado app
class Index(RequestHandler):
    async def get(self):
        self.set_header('Content-Type', 'text/plain')
        self.finish('Hello Tornado!')


def build_app():
    return Application([
        ('/', Index)
    ])


async def test_get_page_source():
    app = build_app()
    server = HTTPServer(app)
    server.listen(0, '127.0.0.1')
    port = list(server._sockets.values())[0].getsockname()[1]
    try:
        async with drivers.context(drivers.FirefoxDriver, TornadoClient) as driver:
            await driver.get(f'http://127.0.0.1:{port}/')
            assert 'Hello Tornado!' in await driver.get_page_source()
    finally:
        server.stop()
