from contextlib import contextmanager

import pytest

from arsenic.actions import Mouse, chain, Keyboard
<<<<<<< HEAD
from arsenic.session import CompatSession
=======
from arsenic.browsers import Firefox
from arsenic.errors import OperationNotSupported
from arsenic.services import Remote
from arsenic.session import CompatSession


@contextmanager
def null_context():
    yield
>>>>>>> refactored legacy action chains, documented keyboard actions

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


async def test_chained_actions(session):
    async def check(actions, expected):
        await session.perform_actions(actions)
        output = await session.get_element('#output')
        assert expected == await output.get_text()

    await session.get('/actions/')
    output = await session.wait_for_element(5, '#output')
    assert '' == await output.get_text()
    mouse = Mouse()
    keyboard = Keyboard()
    canvas = await session.get_element('#canvas')
    ctx = (
        pytest.raises(OperationNotSupported)
        if
        isinstance(session, CompatSession)
        else
        null_context
    )
    with ctx:
        actions = chain(
            mouse.move_to(canvas),
            mouse.down(),
            mouse.move_by(10, 20) & keyboard.down('a'),
            mouse.up(),
            keyboard.up('a'),
        )
        await check(actions, 'a' * 30)
        actions = chain(
            mouse.move_to(canvas),
            mouse.down() & keyboard.down('a'),
            mouse.move_by(10, 20) & keyboard.up('a'),
            mouse.up()
        )
        await check(actions, '')
