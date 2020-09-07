import json
import os
from contextlib import contextmanager
from subprocess import check_call
from typing import Any, AsyncContextManager, Callable, Dict, Optional, Type

import pytest
from asyncio_extras import async_contextmanager
from aiohttp.web import TCPSite, AppRunner

from arsenic import Session, browsers, get_session, services
from tests.utils import find_binary
from .app import build_app
from .utils import null_context


def local_session_factory(
    name: str,
    driver: str,
    service: Type[services.Service],
    browser: Type[browsers.Browser],
    browser_opts: Optional[Dict[str, Any]] = None,
) -> Callable[[str], AsyncContextManager[Session]]:
    browser_opts = browser_opts or {}

    def ctx(root_url: str):
        binary = find_binary(driver)
        return get_session(service(binary=binary), browser(**browser_opts), root_url)

    ctx.__name__ = name
    return ctx


get_ff_session = local_session_factory(
    "get_ff_session",
    "geckodriver",
    services.Geckodriver,
    browsers.Firefox,
    {"moz:firefoxOptions": {"args": ["-headless"]}},
)
get_chrome_session = local_session_factory(
    "get_chrome_session",
    "chromedriver",
    services.Chromedriver,
    browsers.Chrome,
    {"goog:chromeOptions": {"args": ["--headless", "--disable-gpu", "--no-sandbox"]}},
)
get_ie_session = local_session_factory(
    "get_ie_session",
    "IEDriverServer",
    services.IEDriverServer,
    browsers.InternetExplorer,
)


@contextmanager
def bsl_context():
    if "BROWSERSTACK_LOCAL_IDENTIFIER" not in os.environ:
        raise pytest.skip(
            "Browserstack API key set, but no local identifier configured (BROWSERSTACK_LOCAL_IDENTIFIER)"
        )
    binary = find_binary("BrowserStackLocal")
    if not binary:
        raise pytest.skip(
            "Browserstack API key set, but no BrowserStackLocal binary found"
        )
    args = [
        binary,
        "--key",
        os.environ["BROWSERSTACK_API_KEY"],
        "--verbose",
        os.environ.get("BROWSERSTACK_LOCAL_VERBOSITY", "1"),
        "--local-identifier",
        os.environ["BROWSERSTACK_LOCAL_IDENTIFIER"],
        "--daemon",
    ]
    check_call(args + ["start"])
    try:
        yield
    finally:
        check_call(args + ["stop"])


@async_contextmanager
async def get_remote_session(root_url: str):
    if "REMOTE_BROWSER" not in os.environ:
        raise pytest.skip("No remote browser configured (REMOTE_BROWSER)")
    if "REMOTE_SERVICE" not in os.environ:
        raise pytest.skip("No remote service configured (REMOTE_SERVICE)")
    if "BROWSERSTACK_API_KEY" in os.environ:
        context = bsl_context
    else:
        context = null_context
    remote_browser = json.loads(os.environ["REMOTE_BROWSER"])
    browser_cls = getattr(browsers, remote_browser.pop("type"))
    with context():
        async with get_session(
            services.Remote(url=os.environ["REMOTE_SERVICE"]),
            browser_cls(**remote_browser),
            root_url,
        ) as session:
            yield session


@pytest.fixture(
    params=[get_ff_session, get_chrome_session, get_remote_session, get_ie_session],
    ids=lambda func: func.__name__[4:],
)
async def session(root_url, request) -> Session:
    async with request.param(root_url) as session:
        yield session


@pytest.fixture
async def root_url(event_loop):
    application = build_app()
    runner = AppRunner(application)
    await runner.setup()
    site = TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    try:
        for socket in site._server.sockets:
            host, port = socket.getsockname()
            break
        yield f"http://{host}:{port}"
    finally:
        await runner.cleanup()
