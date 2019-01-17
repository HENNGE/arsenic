import pytest

from aiohttp.web import Application, Response

from arsenic import start_session, services, browsers, stop_session

pytestmark = pytest.mark.asyncio


async def index(request):
    data = await request.post()
    name = data.get("name", "World")
    return Response(
        status=200,
        content_type="text/html",
        body=f"""<html>
    <body>
        <h1>Hello {name}</h1>
        <form method='post' action='/'>
            <input name='name' />
            <input type='submit' />
        </form>
    </body>
</html>""",
    )


def build_app():
    app = Application()
    app.router.add_route("*", "/", index)
    return app


@pytest.fixture
async def app(event_loop):
    application = build_app()
    server = await event_loop.create_server(application.make_handler(), "127.0.0.1", 0)
    try:
        for socket in server.sockets:
            host, port = socket.getsockname()
        yield f"http://{host}:{port}"
    finally:
        server.close()


@pytest.fixture
async def session(app):
    session = await start_session(services.Geckodriver(), browsers.Firefox(), bind=app)
    try:
        yield session
    finally:
        await stop_session(session)


async def test_index(session):
    await session.get("/")
    title = await session.wait_for_element(5, "h1")
    text = await title.get_text()
    assert text == "Hello World"
    form_field = await session.get_element('input[name="name"]')
    await form_field.send_keys("test")
    submit = await session.get_element('input[type="submit"]')
    await submit.click()
    title = await session.wait_for_element(5, "h1")
    text = await title.get_text()
    assert text == "Hello test"
