from aiohttp.web import Application, Response, run_app
from pathlib import Path

from jinja2 import FileSystemLoader, Environment

TEMPLATES_DIR = Path(__file__).parent / "templates"


async def process_form(request):
    return {"value": (await request.post()).get("field")}


async def process_cookies(request):
    return {"value": request.cookies.get("test", "")}


async def process_file_form(request):
    data = await request.post()
    return {
        "filename": data["file"].filename,
        "contents": data["file"].file.read().decode("utf-8"),
    }


def render_view(jinja, template, process=None):
    async def view(request):
        data = {}
        if process is not None:
            data = await process(request)
        response = await jinja.get_template(template).render_async(**data)
        return Response(text=response, content_type="text/html")

    return view


def build_app() -> Application:
    app = Application()
    jinja = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), enable_async=True)
    app.router.add_get("/", render_view(jinja, "index.html"))
    app.router.add_get("/html/", render_view(jinja, "form.html"))
    app.router.add_post("/form/", render_view(jinja, "data.html", process_form))
    app.router.add_get("/js/", render_view(jinja, "js.html"))
    app.router.add_get("/cookie/", render_view(jinja, "data.html", process_cookies))
    app.router.add_get("/actions/", render_view(jinja, "actions.html"))
    app.router.add_get("/screenshot/", render_view(jinja, "screenshot.html"))
    app.router.add_get("/file/", render_view(jinja, "file_form.html"))
    app.router.add_post(
        "/file/", render_view(jinja, "file_data.html", process_file_form)
    )
    app.router.add_get("/selectors/", render_view(jinja, "selector_types.html"))
    return app


def main():
    run_app(build_app(), host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
