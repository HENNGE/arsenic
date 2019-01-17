from arsenic.actions import Mouse, chain
from arsenic.session import Element, Session


async def drag_and_drop(
    session: Session, source_element: Element, x_offset: int, y_offset: int
):
    mouse = Mouse()
    actions = chain(
        mouse.move_to(source_element),
        mouse.down(),
        mouse.move_by(x_offset, y_offset),
        mouse.up(),
    )
    await session.perform_actions(actions)


import asyncio
from functools import wraps, partial

from aiohttp.web import Response, Application

from arsenic import get_session, browsers, services


async def handle(request):
    return Response(
        status=200,
        content_type="text/html",
        body="""<html>
<body>
  <input id="range" type="range" min="1" max="100" value="1" /> <span id="output" />
  <script>
    const range = document.getElementById('range');
    const output = document.getElementById('output');
    output.textContent = range.value;
    range.addEventListener('change', event => output.textContent = event.target.value);
    window.INITIALIZED = true;
  </script>
</body>
</html>""",
    )


def build_app():
    app = Application()
    app.router.add_get("/", handle)
    return app


class RunApp:
    def __init__(self):
        self.app = build_app()
        self.server = None

    async def __aenter__(self):
        self.server = await asyncio.get_event_loop().create_server(
            self.app.make_handler(), "127.0.0.1", 0
        )
        for socket in self.server.sockets:
            host, port = socket.getsockname()
        return f"http://{host}:{port}"

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.server:
            self.server.close()


def with_app_and_session(coro):
    @wraps(coro)
    async def wrapper():
        gecko = services.Geckodriver()
        ff = browsers.Firefox()
        async with RunApp() as base_url, get_session(gecko, ff, base_url) as session:
            return await coro(session)

    return wrapper


@with_app_and_session
async def run_drag_and_drop(session):
    values = []
    await session.get("/")
    await session.wait(5, partial(session.execute_script, "return window.INITIALIZED;"))
    result = await session.get_element("#output")
    values.append(await result.get_text())
    source = await session.get_element("#range")
    await drag_and_drop(session, source, 200, 0)
    values.append(await result.get_text())
    return values


def main():
    loop = asyncio.get_event_loop()
    values = loop.run_until_complete(run_drag_and_drop())
    print(f"{values[0]} -> {values[1]}")


if __name__ == "__main__":
    main()
