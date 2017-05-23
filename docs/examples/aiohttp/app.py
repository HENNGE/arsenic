from aiohttp import web


async def handle(request):
    name = request.match_info.get('name', 'Anonymous')
    text = f'<html><body><h1>Hello {name}</h1></body>'
    return web.Response(text=text, content_type='text/html')


def build_app():
    app = web.Application()
    app.router.add_get('/', handle)
    app.router.add_get('/{name}', handle)
    return app


def main():
    app = build_app()
    web.run_app(app)


if __name__ == '__main__':
    main()
