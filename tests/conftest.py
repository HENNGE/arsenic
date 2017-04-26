import attr
import pytest

from arsenic.browsers import Firefox
from arsenic.services import Geckodriver, Remote


@attr.s
class Service:
    driver = attr.ib()
    browser = attr.ib()

DRIVERS = [
    Service(Geckodriver(), Firefox()),
    # Service(Remote('http://localhost:4444/wd/hub'), Firefox())
]


@pytest.fixture(scope='module', params=DRIVERS)
def service(request):
    yield request.param
