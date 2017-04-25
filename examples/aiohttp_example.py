from asyncio import get_event_loop

from aiohttp import web

from arsenic.clients.aiohttp import AiohttpClient

import base

async def run_selenium(port):
    print('Hello Aiohttp!' in await base.run_selenium(port, AiohttpClient))


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