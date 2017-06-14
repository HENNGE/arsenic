import pytest


pytestmark = pytest.mark.asyncio


async def test_get_page_source(session):
    await session.get('/')
    assert 'Hello World!' in await session.get_page_source()


async def test_simple_form_submit(session):
    await session.get('/html/')
    field = await session.wait_for_element(5, 'input[name="field"]')
    await field.send_keys('sample input')
    submit = await session.get_element('input[type="submit"]')
    await submit.click()
    h2 = await session.wait_for_element(5, 'h2')
    assert 'sample input' == await h2.get_text()


async def test_displayed(session):
    await session.get('/js/')
    button = await session.wait_for_element(5, 'button')
    div = await session.wait_for_element(5, '#secret')
    assert not await div.is_displayed()
    await button.click()
    assert await session.wait(5, div.is_displayed)


async def test_execute_script(session):
    await session.get('/js/')
    div = await session.wait_for_element(5, 'div')
    assert not await div.is_displayed()
    await session.execute_script('document.getElementById("secret").removeAttribute("class");')
    assert await session.wait(5, div.is_displayed)


async def test_cookies(session):
    await session.get('/cookie/')
    h2 = await session.wait_for_element(5, 'h2')
    assert '' == await h2.get_text()
    await session.add_cookie('test', 'value')
    await session.get('/cookie/')
    h2 = await session.wait_for_element(5, 'h2')
    assert 'value' == await h2.get_text()
    await session.delete_cookie('test')
    await session.get('/cookie/')
    h2 = await session.wait_for_element(5, 'h2')
    assert '' == await h2.get_text()
