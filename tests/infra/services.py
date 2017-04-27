import attr

from arsenic.browsers import Firefox
from arsenic.services import Geckodriver


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
]
