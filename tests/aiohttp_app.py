from aiohttp import web

from tests.utils import read


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
