import attr

from arsenic.browsers import Firefox
from arsenic.services import Geckodriver, Remote


@attr.s
class ServiceContext:
    driver = attr.ib()
    browser = attr.ib()
    name = attr.ib()


SERVICE_CONTEXTS = [
    ServiceContext(
        driver=Geckodriver(),
        browser=Firefox(),
        name='geckofirefox'
    ),
    ServiceContext(
        driver=Remote('http://firefox:4444/wd/hub'),
        browser=Firefox(),
        name='remotefirefox'
    )
]
