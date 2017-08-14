import pytest

from arsenic import start_session
from arsenic.browsers import Chrome
from arsenic.errors import UnknownError


pytestmark = pytest.mark.asyncio


async def test_chrome_invalid_session(service, browser):
    if not isinstance(browser, Chrome):
        raise pytest.skip('Test for chrome only')

    browser.capabilities['chromeOptions'] = 'these are not valid options'

    with pytest.raises(UnknownError):
        session = await start_session(
            service,
            browser,
        )
