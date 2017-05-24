import pytest

from app import build_app

from arsenic.browsers import Firefox
from arsenic.engines.aiohttp import Aiohttp
from arsenic.services import Geckodriver


@pytest.fixture(scope='function')
def aiohttp_server(event_loop):
    """
    pytest fixture that runs our little aiohttp app on a random port.
    """
    app = build_app()
    handler = app.make_handler()
    server = event_loop.run_until_complete(
        event_loop.create_server(handler, '0.0.0.0', 0)
    )
    try:
        yield server
    finally:
        server.close()
        event_loop.run_until_complete(server.wait_closed())
        event_loop.run_until_complete(app.shutdown())
        event_loop.run_until_complete(handler.shutdown(5))
        event_loop.run_until_complete(app.cleanup())


@pytest.fixture(scope='function')
def arsenic_driver(event_loop, aiohttp_server):
    """
    pytest fixture which depends on the aiohttp_server fixture and runs a 
    Firefox instance bound to the URL of the aiohttp server.
    """
    cleanup = []
    host, port = aiohttp_server.sockets[0].getsockname()
    base_url = f'http://localhost:{port}'
    try:
        # Start geckodriver using aiohttp/asyncio
        driver = event_loop.run_until_complete(
            Geckodriver().start(engine=Aiohttp)
        )
        cleanup.append(driver.close)
        # Create a new session and bind it to our servers base url
        session = event_loop.run_until_complete(
            driver.new_session(
                # Request a Firefox instance
                browser=Firefox(),
                # Bind to the server url
                bind=base_url,
            )
        )
        cleanup.append(session.close)
        yield session
    finally:
        for coro in reversed(cleanup):
            event_loop.run_until_complete(coro())


@pytest.mark.asyncio
async def test_my_app(event_loop, arsenic_driver):
    # Because or driver is bound to the server URL, we only have to provide the
    # path of the URL we wish to navigate to
    await arsenic_driver.get('/')
    # Wait up to 5 seconds for the h1 to appear
    h1 = await arsenic_driver.wait_for_element(5, 'h1')
    # Check that it has the correct text
    assert await h1.get_text() == 'Hello Anonymous'
    # Do the same on the /world resource
    await arsenic_driver.get('/world')
    h1 = await arsenic_driver.wait_for_element(5, 'h1')
    assert await h1.get_text() == 'Hello world'
