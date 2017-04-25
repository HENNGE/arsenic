# Async Selenium

You probably don't want to use this yet, if you want to help out, that'd be great!

## Major differences

* Use `arsenic.drivers.init` or `arsenic.driveres.context` to instantiate webdrivers.
* arsenic is async framework agnostic, so you have to specify which framework you want
  to use when creating a webdriver.
* All API methods on the webdriver are async. For example `await driver.find_element_by_css_selector('.foo')`.
* All property APIs on the webdriver are now methods prefixed with `get_`, and where
  applicable with `set_`. For example `await driver.get_page_source()` instead of `driver.page_source`.
* So far only have a Firefox and Chrome driver, only Firefox is tested.
* **Lots of stuff is probably terribly broken or not implemented yet.**


## Quickstart

### Asyncio/Aiohttp

```python
from asyncio import get_event_loop

from aiohttp import web

from arsenic.clients.aiohttp import AiohttpClient
from arsenic import drivers

async def run_selenium(port):
    async with drivers.context(drivers.ChromeDriver, AiohttpClient) as driver:
        await driver.get(f'http://127.0.0.1:{port}/')
        return await driver.get_page_source()


# Simple Aiohttp app

async def index(request):
    return web.Response(text='Hello Aiohttp!', content_type='text/plain')


def build_app():
    app = web.Application()
    app.router.add_get('/', index)
    return app

async def run(loop):
    app = build_app()
    handler = app.make_handler()
    server = await loop.create_server(handler, '127.0.0.1', 0)
    port = server.sockets[0].getsockname()[1]
    try:
        await run_selenium(port)
    finally:
        server.close()
        await server.wait_closed()
        await app.shutdown()
        await handler.shutdown(10)
        await app.cleanup()


def main():
    loop = get_event_loop()
    loop.run_until_complete(run(loop))


if __name__ == '__main__':
    main()
```

### Tornado

```python

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from arsenic.clients.tornado import TornadoClient
import base


async def run_selenium(port):
    async with drivers.context(drivers.ChromeDriver, TornadoClient) as driver:
        await driver.get(f'http://127.0.0.1:{port}/')
        return await driver.get_page_source()


# Simple Tornado app
class Index(RequestHandler):
    async def get(self):
        self.set_header('Content-Type', 'text/plain')
        self.finish('Hello Tornado!')


def build_app():
    return Application([
        ('/', Index)
    ])

async def run():
    app = build_app()
    server = HTTPServer(app)
    server.listen(0, '127.0.0.1')
    port = list(server._sockets.values())[0].getsockname()[1]
    try:
        await run_selenium(port)
    finally:
        server.stop()


def main():
    loop = IOLoop.current()
    loop.run_sync(run)


if __name__ == '__main__':
    main()
```
