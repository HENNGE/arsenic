import os
from urllib.parse import urlparse, parse_qsl, urlunparse

import attr
import shutil

from arsenic.browsers import Firefox
from arsenic.services import Geckodriver, Remote


BROWSERS = {
    'firefox': Firefox,
}


@attr.s
class ServiceContext:
    driver = attr.ib()
    browser = attr.ib()
    name = attr.ib()


SERVICE_CONTEXTS = []


if shutil.which('geckodriver'):
    SERVICE_CONTEXTS.append(ServiceContext(
        driver=Geckodriver(),
        browser=Firefox(),
        name='geckofirefox'
    ))


def get_remote_drivers(remotes):
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
            yield ServiceContext(
                driver=Remote(unparsed),
                browser=browser(**query),
                name=f'remote{browsername}'
            )


remotes = os.environ.get('REMOTE_WEBDRIVERS', None)


if remotes is not None:
    SERVICE_CONTEXTS.extend(get_remote_drivers(remotes))
