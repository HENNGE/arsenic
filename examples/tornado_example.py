from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from arsenic.clients.tornado import TornadoClient
import base


async def run_selenium(port):
    print('Hello Tornado!' in await base.run_selenium(port, TornadoClient))


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
