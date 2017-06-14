from aiohttp.web import Application, Response, run_app
from pathlib import Path

from jinja2 import FileSystemLoader, Environment

TEMPLATES_DIR = Path(__file__).parent / 'templates'


async def process_form(request):
    return {'value': (await request.post()).get('field')}

async def process_cookies(request):
    return {'value': request.cookies.get('test', '')}


def render_view(jinja, template, process=None):
    async def view(request):
        data = {}
        if process is not None:
            data = await process(request)
        response = await jinja.get_template(template).render_async(**data)
        return Response(text=response, content_type='text/html')
    return view


def build_app() -> Application:
    app = Application()
    jinja = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        enable_async=True,
    )
    app.router.add_get('/', render_view(jinja, 'index.html'))
    app.router.add_get('/html/', render_view(jinja, 'form.html'))
    app.router.add_post('/form/', render_view(jinja, 'data.html', process_form))
    app.router.add_get('/js/', render_view(jinja, 'js.html'))
    app.router.add_get('/cookie/', render_view(jinja, 'data.html', process_cookies))
    return app


def main():
    run_app(build_app(), host='127.0.0.1', port=5000)

if __name__ == "__main__":
    main()
