import os
from urllib.parse import parse_qsl, urlparse

import attr
import pytest

from arsenic import browsers, services, start_session, stop_session


@attr.s
class BrowserContext:
    service = attr.ib()
    browser = attr.ib()
    base_url = attr.ib(default=None)


def get_instance(config, module):
    parse_result = urlparse(config)
    cls = getattr(module, parse_result.path)
    kwargs = {
        key: value if value else True
        for key, value in
        parse_qsl(parse_result.query, keep_blank_values=True)
    }
    return cls(**kwargs)


@pytest.fixture()
def session_context(web_app):
    service = get_instance(os.environ['ARSENIC_SERVICE'], services)
    browser = get_instance(os.environ['ARSENIC_BROWSER'], browsers)
    base_url = os.environ['ARSENIC_BASE_URL'] if os.environ.get('ARSENIC_REMOTE', '0') == '1' else web_app
    return BrowserContext(
        service=service,
        browser=browser,
        base_url=base_url
    )


@pytest.fixture()
async def session(session_context):
    session = await start_session(
        session_context.service,
        session_context.browser,
        bind=session_context.base_url
    )
    session.browser = session_context.browser
    session.service = session_context.service
    try:
        yield session
    finally:
        await stop_session(session)
