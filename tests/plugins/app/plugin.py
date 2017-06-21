import pytest

from .app import build_app


@pytest.fixture
async def web_app(event_loop):
    application = build_app()
    server = await event_loop.create_server(
        application.make_handler(),
        '127.0.0.1',
        0
    )
    try:
        for socket in server.sockets:
            host, port = socket.getsockname()
        yield f'http://{host}:{port}'
    finally:
        server.close()
