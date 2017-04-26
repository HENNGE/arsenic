import pytest

from arsenic.engines.tornado import Tornado
from tests.tornado_app import build_app


pytestmark = pytest.mark.gen_test(timeout=30, run_sync=False)


@pytest.fixture()
def app():
    return build_app()


async def test_get_page_source(base_url, service, http_server):
    async with service.driver.run(Tornado) as driver:
        async with driver.session(service.browser) as session:
            await session.get(f'{base_url}/')
            assert 'Hello Tornado!' in await session.get_page_source()


async def test_simple_form_submit(base_url, service, http_server):
    async with service.driver.run(Tornado) as driver:
        async with driver.session(service.browser) as session:
            await session.get(f'{base_url}/html/')
            field = await session.get_element('input[name="field"]')
            await field.send_keys('sample input')
            submit = await session.get_element('input[type="submit"]')
            await submit.click()
            assert 'sample input' in await session.get_page_source()
