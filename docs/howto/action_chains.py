from arsenic.actions import Mouse, chain
from arsenic.session import Element, Session


async def drag_and_drop(session: Session, source_element: Element, x_offset: int, y_offset: int):
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


async def handle_dnd(request):
    return Response(status=200, content_type='text/html', body='''<html>
<head>
  <style>
    #wrapper {
      border: cyan 1px solid;
      width: 500px;
      height: 500px;
    }
    #draggable {
      position: absolute;
      left: 0;
      top: 0;
      width: 100px;
      height: 100px;
      border: pink 1px solid;
    }
</style>
</head>
<body>
  <div id='wrapper'>
    <div id='draggable' draggable='true'>Draggable</div>
  </div>
  <script>
    const draggable = document.getElementById('draggable');
    const int = x => parseInt(x, 10);
    const gpvi = (s, p) => int(s.getPropertyValue(p));
    draggable.addEventListener('dragstart', event => {
        const style = window.getComputedStyle(event.target, null);
        event.dataTransfer.setData(
            'text/plain',
            JSON.stringify([gpvi(style, 'left') - event.clientX, gpvi(style, 'top') - event.clientY])
        );
    }, false);
    document.body.addEventListener('dragover', event => {
        event.preventDefault();
        return false;
    }, false);
    document.body.addEventListener('drop', event => {
        const [offset_left, offset_top] = JSON.parse(event.dataTransfer.getData('text/plain'));
        draggable.style.left = `${event.clientX + offset_left}px`;
        draggable.style.top = `${event.clientY + offset_top}px`;
        event.preventDefault();
        return false;
    }, false);
    window.INITIALIZED = true;
  </script>
</body>
</html>''')


def build_app():
    app = Application()
    app.router.add_get('/', handle_dnd)
    return app


class RunApp:
    def __init__(self):
        self.app = build_app()
        self.server = None

    async def __aenter__(self):
        self.server = await asyncio.get_event_loop().create_server(
            self.app.make_handler(),
            '127.0.0.1',
            0
        )
        for socket in self.server.sockets:
            host, port = socket.getsockname()
        return f'http://{host}:{port}'

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
    await session.get('/')
    await session.wait(5, partial(session.execute_script, 'return window.INITIALIZED;'))
    source = await session.get_element('#draggable')
    await drag_and_drop(session, source, 100, 100)
    await asyncio.sleep(10)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_drag_and_drop())


if __name__ == '__main__':
    main()
