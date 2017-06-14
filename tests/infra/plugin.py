import os
import shutil
import sys
from urllib.parse import parse_qsl, urlparse, urlunparse

import attr
import pytest

from arsenic import browsers, services, start_session, stop_session

BROWSERS = {
    'firefox': browsers.Firefox,
    'ie': browsers.InternetExplorer,
}


@attr.s
class BrowserContext:
    service = attr.ib()
    browser = attr.ib()
    name = attr.ib()
    base_url = attr.ib(default=None)


def get_remote_drivers(remotes):
    if 'WEB_APP_BASE_URL' not in os.environ:
        return
    for remote in remotes.split(' '):
        parsed = urlparse(remote)
        query = dict(parse_qsl(parsed.query))
        browser_name = query.pop('browser', None)
        browser = BROWSERS.get(browser_name, None)
        if browser is not None:
            unparsed = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                '',
                '',
                ''
            ))
            yield BrowserContext(
                service=services.Remote(unparsed),
                browser=browser(**query),
                base_url=os.environ['WEB_APP_BASE_URL'],
                name=f'remote-{browser_name}',
            )


def gather_browsers():
    if shutil.which('geckodriver'):
        yield BrowserContext(
            services.Geckodriver(log_file=sys.stdout),
            browsers.Firefox(),
            'geckodriver-firefox',
        )
    if shutil.which('phantomjs'):
        yield BrowserContext(
            services.PhantomJS(log_file=sys.stdout),
            browsers.PhantomJS(),
            'phantomjs-phantomjs',
        )
    remotes = os.environ.get('REMOTE_WEBDRIVERS', None)
    if remotes:
        yield from get_remote_drivers(remotes)


def pytest_generate_tests(metafunc):
    if 'session' in metafunc.fixturenames:
        fixtures = list(gather_browsers())
        metafunc.parametrize(
            'session',
            fixtures,
            indirect=True,
            ids=[ctx.name for ctx in fixtures]
        )


@pytest.fixture(scope='module')
async def session(request, web_app):
    ctx = request.param
    bind = ctx.base_url or web_app
    session = await start_session(ctx.service, ctx.browser, bind=bind)
    try:
        yield session
    finally:
        await stop_session(session)
