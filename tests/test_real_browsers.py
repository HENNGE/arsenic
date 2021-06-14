import secrets
from pathlib import Path
from typing import List, Any, Dict

import pytest
from PIL import Image

from arsenic.actions import Keyboard, Mouse, chain
from arsenic.browsers import Firefox
from arsenic.connection import RemoteConnection
from arsenic.constants import SelectorType, WindowType
from arsenic.errors import NoSuchElement
from arsenic.utils import Rect

pytestmark = [pytest.mark.asyncio]


async def test_get_page_source(session):
    await session.get("/")
    assert "Hello World!" in await session.get_page_source()


async def test_element_not_found(session):
    await session.get("/")
    with pytest.raises(NoSuchElement):
        await session.get_element("h2")


async def test_simple_form_submit(session):
    await session.get("/html/")
    field = await session.wait_for_element(5, 'input[name="field"]')
    await field.send_keys("sample input")
    submit = await session.get_element('input[type="submit"]')
    await submit.click()
    h2 = await session.wait_for_element(5, "h2")
    assert "sample input" == await h2.get_text()


@pytest.mark.parametrize(
    "using,selector,result",
    [
        (SelectorType.css_selector, ".classname", "Class Name"),
        (SelectorType.link_text, "link text", "link text"),
        (SelectorType.partial_link_text, "partial", "partial link text"),
        (SelectorType.tag_name, "h2", "Title Here"),
        (SelectorType.xpath, ".//h2", "Title Here"),
    ],
)
async def test_selector_types(session, using, selector, result):
    await session.get("/selectors/")
    element = await session.wait_for_element(5, selector, using)
    assert result == await element.get_text()


async def test_displayed(session):
    await session.get("/js/")
    button = await session.wait_for_element(5, "button")
    div = await session.wait_for_element(5, "#secret")
    assert not await div.is_displayed()
    await button.click()
    assert await session.wait(5, div.is_displayed)


async def test_execute_script(session):
    await session.get("/js/")
    div = await session.wait_for_element(5, "div")
    assert not await div.is_displayed()
    await session.execute_script(
        'document.getElementById("secret").removeAttribute("class");'
    )
    assert await session.wait(5, div.is_displayed)


async def test_cookies(session):
    await session.get("/cookie/")
    h2 = await session.wait_for_element(5, "h2")
    assert "" == await h2.get_text()
    await session.add_cookie("test", "value")
    await session.get("/cookie/")
    h2 = await session.wait_for_element(5, "h2")
    assert "value" == await h2.get_text()
    await session.delete_cookie("test")
    await session.get("/cookie/")
    h2 = await session.wait_for_element(5, "h2")
    assert "" == await h2.get_text()


async def test_chained_actions(session):
    if isinstance(session.browser, Firefox) and isinstance(
        session.driver.connection, RemoteConnection
    ):
        raise pytest.skip("remote firefox actions do not work")

    async def check(actions, expected):
        await session.perform_actions(actions)
        output = await session.get_element("#output")
        assert expected == await output.get_text()

    await session.get("/actions/")
    output = await session.wait_for_element(5, "#output")
    assert "" == await output.get_text()

    await session.get("/actions/")

    output = await session.wait_for_element(5, "#output")
    assert "" == await output.get_text()

    mouse = Mouse()
    keyboard = Keyboard()
    canvas = await session.get_element("#canvas")

    actions = chain(
        mouse.move_to(canvas),
        mouse.down() & keyboard.down("a"),
        mouse.move_by(10, 20) & keyboard.up("a"),
        mouse.up(),
    )
    await check(actions, "")

    actions = chain(
        mouse.move_to(canvas),
        mouse.down(),
        mouse.move_by(10, 20) & keyboard.down("a"),
        mouse.up(),
        keyboard.up("a"),
    )
    await check(actions, "a" * 30)

    actions = chain(
        mouse.move_to(canvas),
        mouse.down() & keyboard.down("a"),
        mouse.move_by(10, 20) & keyboard.up("a"),
        mouse.up(),
    )
    await check(actions, "")


async def test_get_screenshot(session):
    await session.get("/screenshot/")
    rect = await session.wait_for_element(5, "#rect")
    screenshot = await session.get_screenshot()
    image = Image.open(screenshot)
    info = await rect.get_rect()
    rect_img = image.crop((info.x, info.y, info.x + info.height, info.y + info.width))
    colors = rect_img.getcolors()
    assert len(colors) == 1
    count, color = colors[0]
    assert count == int(info.width * info.height)
    assert color == (254, 220, 186, 255)


async def test_get_rect(session):
    await session.get("/screenshot/")
    ele = await session.get_element("#rect")
    rect = await ele.get_rect()
    assert rect == Rect(0, 0, 100, 100)


async def test_file_upload(session, tmpdir):
    path = Path(str(tmpdir)) / "file.txt"
    payload = secrets.token_urlsafe()
    with path.open("w") as fobj:
        fobj.write(payload)
    await session.get("/file/")
    file_input = await session.wait_for_element(5, 'input[name="file"]')
    await file_input.send_file(path)
    submit_input = await session.get_element('input[type="submit"]')
    await submit_input.click()
    contents_span = await session.wait_for_element(5, "#contents")
    assert payload == await contents_span.get_text()


async def test_change_window(session):
    handles = await session.get_window_handles()
    assert len(handles) == 1
    for i in range(4):
        await session.execute_script("window.open();")

    async def checker():
        handles = await session.get_window_handles()
        if len(handles) == 5:
            return handles
        return False

    handles = await session.wait(5, checker)
    await session.switch_to_window(handles[2])
    current = await session.get_window_handle()
    assert current == handles[2]


async def test_request(session):
    url = "/window/handles"
    handles = await session.request(url)
    assert len(handles) == 1


@pytest.mark.parametrize("window_type", [WindowType.tab, WindowType.window])
async def test_new_window(session, window_type):
    new_window_data: Dict[str, Any] = await session.new_window(window_type)
    assert new_window_data["type"] == window_type.value
    new_handle: str = new_window_data["handle"]
    handles: List[str] = await session.get_window_handles()
    assert new_handle in handles
    assert len(handles) == 2
