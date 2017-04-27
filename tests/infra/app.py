from asyncio import get_event_loop
from functools import wraps

import attr
from aiohttp import web as aiohttp_web
from tornado import web as tornado_web
from tornado.httpserver import HTTPServer

from tests.infra.utils import read


@attr.s
class SimpleRequest:
    method = attr.ib()
    params = attr.ib()
    form = attr.ib(default=None)


@attr.s
class Route:
    path = attr.ib()
    method = attr.ib()
    handler = attr.ib()


@attr.s
class AppContext:
    port = attr.ib()
    stop = attr.ib()


async def index(request):
    return 'Hello World!'


async def html(request):
    return read('simple.html')


async def form(request):
    return read('formdata.html').format(value=request.form['field'])


ROUTES = [
    Route('/', 'GET', index),
    Route('/html/', 'GET', html),
    Route('/form/', 'POST', form),
]


def aiohttp_adapter(handler):
    @wraps(handler)
    async def wrapper(request):
        method = request.method
        if method == 'POST':
            form = await request.post()
        else:
            form = None
        params = request.query
        response = await handler(SimpleRequest(method, params, form))
        return aiohttp_web.Response(text=response, content_type='text/html')
    return wrapper


def tornado_adapter(handler):
    class Handler(tornado_web.RequestHandler):
        async def get(self):
            await self.handle('GET')

        async def post(self):
            await self.handle('POST')

        async def handle(self, method):
            params = self.request.query_arguments
            form = None if method == 'GET' else {
                key: values[0]
                for key, values in self.request.body_arguments.items()
            }
            response = await handler(SimpleRequest(method, params, form))
            self.finish(response)
    return Handler


def build_aiohttp_app():
    app = aiohttp_web.Application()
    for route in ROUTES:
        app.router.add_route(
            method=route.method,
            path=route.path,
            handler=aiohttp_adapter(route.handler)
        )
    return app


def build_tornado_app():
    return tornado_web.Application([
        (route.path, tornado_adapter(route.handler))
        for route in ROUTES
    ])


async def start_aiohttp_app():
    app = build_aiohttp_app()
    handler = app.make_handler()
    server = await get_event_loop().create_server(handler, '127.0.0.1', 0)
    port = server.sockets[0].getsockname()[1]

    def stop():
        async def inner():
            server.close()
            await server.wait_closed()
            await app.shutdown()
            await handler.shutdown(10)
            await app.cleanup()
        get_event_loop().run_until_complete(inner())

    return AppContext(port, stop)


async def start_tornado_app():
    app = build_tornado_app()
    server = HTTPServer(app)
    server.listen(0, '127.0.0.1')
    port = list(server._sockets.values())[0].getsockname()[1]

    def stop():
        server.stop()

    return AppContext(port, stop)
