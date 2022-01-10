import base64
from functools import partial
from io import BytesIO
from pathlib import Path
from typing import Awaitable, Callable, Any, List, Dict, Tuple, Iterator

import attr

from arsenic import constants
from arsenic.connection import Connection, unwrap
from arsenic.constants import SelectorType, WindowType
from arsenic.errors import NoSuchElement, OperationNotSupported
from arsenic.utils import Rect

UNSET = object()


def escape_value(value: str) -> str:
    if '"' in value and "'" in value:
        parts = value.split('"')
        result = ["concat("]
        for part in parts:
            result.append(f'"{part}"')
            result.append(", '\"', ")
        result = result[0:-1]
        if value.endswith('"'):
            return "".join(result) + ")"
        else:
            return "".join(result[:-1]) + ")"
    elif '"' in value:
        return f"'{value}'"
    else:
        return f'"{value}"'


class RequestHelpers:
    async def _request(
        self, *, url: str, method: str, data=None, raw=False, timeout=None
    ):
        status, data = await self.connection.request(
            url=url, method=method, data=data, timeout=timeout
        )
        if raw:
            return data
        if data:
            return self._unwrap(data.get("value", None))

    def _unwrap(self, value):
        """
        Unwrap a value returned from a webdriver. Specifically this means trying to
        extract the element ID of a web element or a list of web elements.
        """
        return unwrap(value)


class Element(RequestHelpers):
    def __init__(self, id: str, connection: Connection, session: "Session"):
        self.id = id
        self.connection = connection
        self.session = session

    async def get_text(self) -> str:
        return await self._request(url="/text", method="GET")

    async def send_keys(self, keys: str):
        await self._request(
            url="/value", method="POST", data={"value": list(keys), "text": keys}
        )

    async def send_file(self, path: Path):
        path = await self.session.connection.upload_file(path)
        await self.send_keys(str(path))

    async def clear(self):
        await self._request(url="/clear", method="POST")

    async def click(self):
        await self._request(url="/click", method="POST")

    async def is_displayed(self) -> bool:
        return await self._request(url="/displayed", method="GET")

    async def is_enabled(self) -> bool:
        return await self._request(url="/enabled", method="GET")

    async def get_attribute(self, name: str) -> str:
        return await self._request(url=f"/attribute/{name}", method="GET")

    async def get_property(self, name: str) -> str:
        return await self._request(url=f"/property/{name}", method="GET")

    async def get_css_value(self, name: str) -> str:
        return await self._request(url=f"/css/{name}", method="GET")

    async def select_by_value(self, value: str):
        value = escape_value(value)
        option = await self.get_element(f"option[value={value}]")
        await option.click()

    async def get_element(
        self, selector: str, selector_type: SelectorType = SelectorType.css_selector
    ) -> "Element":
        element_id = await self._request(
            url="/element",
            method="POST",
            data={"using": selector_type.value, "value": selector},
        )
        return self.session.create_element(element_id)

    async def get_elements(
        self, selector: str, selector_type: SelectorType = SelectorType.css_selector
    ) -> List["Element"]:
        element_ids = await self._request(
            url="/elements",
            method="POST",
            data={"using": selector_type.value, "value": selector},
        )
        return [self.session.create_element(element_id) for element_id in element_ids]

    async def get_rect(self):
        data = await self._request(url="/rect", method="GET")
        return Rect(data["x"], data["y"], data["width"], data["height"])

    async def get_screenshot(self):
        return BytesIO(
            base64.b64decode(await self._request(url="/screenshot", method="GET"))
        )


TCallback = Callable[..., Awaitable[Any]]
TWaiter = Callable[[int, TCallback], Awaitable[Any]]


class Session(RequestHelpers):
    element_class = Element

    def __init__(
        self, connection: Connection, wait: TWaiter, driver, browser, bind: str = ""
    ):
        self.connection = connection
        self.bind = bind
        self.wait = wait
        self.driver = driver
        self.browser = browser

    async def request(
        self, url: str, method: str = "GET", data: Dict[str, Any] = UNSET
    ):
        return await self._request(url=url, method=method, data=data)

    async def get(self, url: str, timeout=None):
        await self._request(
            url="/url", method="POST", data={"url": self.bind + url}, timeout=timeout
        )

    async def get_url(self):
        return await self._request(url="/url", method="GET")

    async def get_page_source(self) -> str:
        return await self._request(url="/source", method="GET")

    async def get_element(
        self, selector: str, selector_type: SelectorType = SelectorType.css_selector
    ) -> Element:
        element_id = await self._request(
            url="/element",
            method="POST",
            data={"using": selector_type.value, "value": selector},
        )
        return self.create_element(element_id)

    async def get_elements(
        self, selector: str, selector_type: SelectorType = SelectorType.css_selector
    ) -> List[Element]:
        result = await self._request(
            url="/elements",
            method="POST",
            data={"using": selector_type.value, "value": selector},
        )
        return [self.create_element(element_id) for element_id in result]

    async def wait_for_element(
        self,
        timeout: int,
        selector: str,
        selector_type: SelectorType = SelectorType.css_selector,
    ) -> Element:
        return await self.wait(
            timeout, partial(self.get_element, selector, selector_type), NoSuchElement
        )

    async def wait_for_element_gone(
        self,
        timeout: int,
        selector: str,
        selector_type: SelectorType = SelectorType.css_selector,
    ):
        async def callback():
            try:
                await self.get_element(selector, selector_type)
            except NoSuchElement:
                return True
            else:
                return False

        return await self.wait(timeout, callback)

    async def add_cookie(
        self,
        name: str,
        value: str,
        *,
        path: str = UNSET,
        domain: str = UNSET,
        secure: bool = UNSET,
        expiry: int = UNSET,
        httponly: bool = UNSET,
    ):
        cookie = {"name": name, "value": value}
        if path is not UNSET:
            cookie["path"] = path
        if domain is not UNSET:
            cookie["domain"] = domain
        if secure is not UNSET:
            cookie["secure"] = secure
        if expiry is not UNSET:
            cookie["expiry"] = expiry
        if httponly is not UNSET:
            cookie["HttpOnly"] = httponly
        await self._request(url="/cookie", method="POST", data={"cookie": cookie})

    async def get_cookie(self, name: str):
        return await self._request(url=f"/cookie/{name}", method="GET")

    async def get_all_cookies(self):
        return await self._request(url="/cookie", method="GET")

    async def delete_cookie(self, name: str):
        await self._request(url=f"/cookie/{name}", method="DELETE")

    async def delete_all_cookies(self):
        await self._request(url="/cookie", method="DELETE")

    async def execute_script(self, script: str, *args: Any):
        return await self._request(
            url="/execute/sync",
            method="POST",
            data={"script": script, "args": list(args)},
        )

    async def execute_async_script(self, script: str, *args: Any):
        return await self._request(
            url="/execute/async",
            method="POST",
            data={"script": script, "args": list(args)},
        )

    async def set_window_size(self, width: int, height: int, handle: str = "current"):
        return await self._request(
            url="/window/rect",
            method="POST",
            data={"width": width, "height": height, "windowHandle": handle},
        )

    async def get_window_size(self, handle: str = "current") -> Tuple[int, int]:
        return await self._request(
            url="/window/rect", method="GET", data={"windowHandle": handle}
        )

    async def set_window_fullscreen(self, handle: str = "current"):
        return await self._request(
            url="/window/fullscreen", method="POST", data={"windowHandle": handle}
        )

    async def set_window_maximize(self, handle: str = "current"):
        return await self._request(
            url="/window/maximize", method="POST", data={"windowHandle": handle}
        )

    async def get_alert_text(self) -> str:
        return await self._request(url="/alert/text", method="GET")

    async def send_alert_text(self, value: str):
        return await self._request(
            url="/alert/text", method="POST", data={"text": value}
        )

    async def dismiss_alert(self):
        return await self._request(url="/alert/dismiss", method="POST")

    async def accept_alert(self):
        return await self._request(url="/alert/accept", method="POST")

    async def perform_actions(self, actions: Dict[str, Any]):
        return await self._request(url="/actions", method="POST", data=actions)

    async def get_screenshot(self) -> BytesIO:
        return BytesIO(
            base64.b64decode(await self._request(url="/screenshot", method="GET"))
        )

    async def close(self):
        await self._request(url="", method="DELETE")

    def create_element(self, element_id):
        return self.element_class(
            element_id, self.connection.prefixed(f"/element/{element_id}"), self
        )

    async def get_window_handles(self):
        return await self._request(url="/window/handles", method="GET")

    async def get_window_handle(self):
        return await self._request(url="/window", method="GET")

    async def switch_to_window(self, handle):
        return await self._request(
            url="/window", method="POST", data={"handle": handle, "name": handle}
        )

    async def new_window(self, window_type: WindowType = WindowType.tab):
        return await self._request(
            url="/window/new", method="POST", data={"type": window_type.value}
        )


def _pointer_down(device, action):
    del action["duration"]
    url = (
        "/buttondown"
        if device["parameters"]["pointerType"] == "mouse"
        else "/touch/down"
    )
    return url, "POST", action


def _pointer_up(device, action):
    del action["duration"]
    url = "/buttonup" if device["parameters"]["pointerType"] == "mouse" else "/touch/up"
    return url, "POST", action


def _pointer_move(device, action):
    del action["duration"]
    url = "/moveto" if device["parameters"]["pointerType"] == "mouse" else "/touch/move"
    origin = action["origin"]
    if origin == "pointer":
        data = {"xoffset": action["x"], "yoffset": action["y"]}
    elif constants.WEB_ELEMENT in origin:
        data = {"element": origin[constants.WEB_ELEMENT]}
    else:
        raise OperationNotSupported(f"Cannot move using origin {origin}")
    return url, "POST", data


def _pause(device, action):
    return None


def key_down(device, action):
    return "/keydown", "POST", {""}


legacy_actions = {
    ("pointer", "pointerDown"): _pointer_down,
    ("pointer", "pointerUp"): _pointer_up,
    ("pointer", "pointerMove"): _pointer_move,
    ("pointer", "pause"): _pause,
    ("key", "pause"): _pause,
}


@attr.s
class LegacyAction:
    device = attr.ib()
    action = attr.ib()


def get_legacy_actions(devices: List[Dict[str, Any]]) -> Iterator[LegacyAction]:
    i = 0
    while devices:
        for device in devices:
            action = device["actions"].pop(0)
            i += 1
            yield LegacyAction(device, action)
        devices = [device for device in devices if device["actions"]]


def transform_legacy_actions(
    devices: List[Dict[str, Any]]
) -> Iterator[Tuple[str, str, Dict[str, Any]]]:
    for legacy_action in get_legacy_actions(devices):
        device_type = legacy_action.device["type"]
        action_type = legacy_action.action["type"]
        device = {
            key: value for key, value in legacy_action.device.items() if key != "type"
        }
        action = {
            key: value for key, value in legacy_action.action.items() if key != "type"
        }
        try:
            handler = legacy_actions[(device_type, action_type)]
        except KeyError:
            raise OperationNotSupported(
                f"Unsupported action {action_type} for device_type {device_type}"
            )
        action = handler(device, action)
        if action is not None:
            yield action
