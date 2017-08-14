import asyncio
import json
import os
from asyncio.subprocess import Process
from functools import partial
from urllib.parse import parse_qsl, urlparse

import attr
import pytest

from arsenic import browsers, services, start_session, stop_session
from arsenic.webdriver import WebDriver


@attr.s
class BrowserContext:
    service = attr.ib()
    browser = attr.ib()
    base_url = attr.ib(default=None)


def maybe_json(value):
    try:
        return json.loads(value)
    except:
        return value


def get_instance(config, module):
    parse_result = urlparse(config)
    cls = getattr(module, parse_result.path)
    kwargs = {
        key: maybe_json(value) if value else True
        for key, value in
        parse_qsl(parse_result.query, keep_blank_values=True)
    }
    return cls(**kwargs)


async def browserstack_local(binary, key, identifier, command):
    process = await asyncio.create_subprocess_exec(
        binary,
        '--key', key,
        '--local-identifier', identifier,
        '--daemon', command,
    )
    _, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(stderr)


@attr.s
class BrowserStackLocal:
    service: services.Service = attr.ib()
    identifier: str = attr.ib(init=False, repr=False)
    api_key: str = attr.ib(init=False, repr=False)
    binary: str = attr.ib(init=False)
    process: Process = attr.ib(default=None, repr=False)

    def __attrs_post_init__(self):
        self.identifier = os.environ['BROWSERSTACK_LOCAL_IDENTIFIER']
        self.api_key = os.environ['BROWSERSTACK_API_KEY']
        self.binary = os.environ.get('BROWSERSTACK_BINARY', 'BrowserStackLocal')

    async def start(self) -> WebDriver:
        await browserstack_local(self.binary, self.api_key, self.identifier, 'start')

        webdriver: WebDriver = await self.service.start()
        webdriver.closers.append(
            partial(browserstack_local, self.binary, self.api_key, self.identifier, 'stop')
        )
        return webdriver


@pytest.fixture()
def service():
    service = get_instance(os.environ['ARSENIC_SERVICE'], services)
    if os.environ.get('BROWSERSTACK_LOCAL_IDENTIFIER', None):
        if not os.environ.get('BROWSERSTACK_API_KEY', False):
            raise pytest.skip('BROWSERSTACK_API_KEY not set')
        service = BrowserStackLocal(service)
    return service


@pytest.fixture()
def browser(web_app, request):
    browser = get_instance(os.environ['ARSENIC_BROWSER'], browsers)
    if os.environ.get('BROWSERSTACK_LOCAL_IDENTIFIER', None):
        if not os.environ.get('BROWSERSTACK_API_KEY', False):
            raise pytest.skip('BROWSERSTACK_API_KEY not set')
        browser.capabilities['name'] = request.node.name
    return browser


@pytest.fixture()
def base_url(web_app):
    return os.environ.get('ARSENIC_BASE_URL', web_app)


@pytest.fixture()
async def session(service, browser, base_url):
    session = await start_session(
        service,
        browser,
        bind=base_url
    )
    session.browser = browser
    session.service = service
    try:
        yield session
    finally:
        await stop_session(session)
