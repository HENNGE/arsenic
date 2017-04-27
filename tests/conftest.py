import itertools

import attr
import pytest

from tests.infra.engines import ENGINE_CONTEXTS
from tests.infra.services import SERVICE_CONTEXTS
from tests.infra.utils import ids_from_params


@attr.s
class TestContext:
    engine_context = attr.ib()
    service_context = attr.ib()


PARAMS = list(itertools.product(ENGINE_CONTEXTS, SERVICE_CONTEXTS))
IDS = list(ids_from_params(PARAMS))


@pytest.fixture(scope='module', params=PARAMS, ids=IDS)
def context(request):
    engine, service = request.param
    yield TestContext(
        engine_context=engine,
        service_context=service
    )

pytest_plugins = "tests.infra.plugin",
