from functools import partial
from pathlib import Path
from typing import Awaitable, Callable, Any, List, Dict, Tuple, Iterator

import attr
import itertools

from arsenic.connection import Connection, WEB_ELEMENT
from arsenic.errors import NoSuchElement, OperationNotSupported

UNSET = object()


def escape_value(value: str) -> str:
    if '"' in value and "'" in value:
        parts = value.split('"')
        result = ['concat(']
        for part in parts:
            result.append(f'"{part}"')
            result.append(', \'"\', ')
        result = result[0:-1]
        if value.endswith('"'):
            return ''.join(result) + ')'
        else:
            return ''.join(result[:-1]) + ')'
    elif '"' in value:
        return f"'{value}'"
    else:
        return f'"{value}"'


class Element:
    def __init__(self, id: str, connection: Connection, session: 'Session'):
        self.id = id
        self.connection = connection
        self.session = session

    async def get_text(self) -> str:
        return await self.connection.request(
            url='/text',
            method='GET'
        )

    async def send_keys(self, keys: str):
        await self.connection.request(
            url='/value',
            method='POST',
            data={
                'value': list(keys),
                'text': keys,
            }
        )

    async def send_file(self, path: Path):
        path = await self.session.connection.upload_file(path)
        await self.send_keys(str(path))

    async def clear(self):
        await self.connection.request(
            url='/clear',
            method='POST'
        )

    async def click(self):
        await self.connection.request(
            url='/click',
            method='POST'
        )

    async def is_displayed(self) -> bool:
        return await self.connection.request(
            url='/displayed',
            method='GET'
        )

    async def is_enabled(self) -> bool:
        return await self.connection.request(
            url='/enabled',
            method='GET'
        )

    async def get_attribute(self, name: str) -> str:
        return await self.connection.request(
            url=f'/attribute/{name}',
            method='GET'
        )

    async def select_by_value(self, value: str):
        value = escape_value(value)
        option = await self.get_element(f'option[value={value}]')
        await option.click()

    async def get_element(self, selector: str) -> 'Element':
        element_id = await self.connection.request(
            url='/element',
            method='POST',
            data={
                'using': 'css selector',
                'value': selector,
            }
        )
        return self.session.create_element(element_id)

    async def get_elements(self, selector: str) -> List['Element']:
        element_ids = await self.connection.request(
            url='/elements',
            method='POST',
            data={
                'using': 'css selector',
                'value': selector,
            }
        )
        return [self.session.create_element(element_id) for element_id in element_ids]


TCallback = Callable[..., Awaitable[Any]]
TWaiter = Callable[[int, TCallback], Awaitable[Any]]


class Session:
    element_class = Element

    def __init__(self, connection: Connection, wait: TWaiter, driver, bind: str=''):
        self.connection = connection
        self.bind = bind
        self.wait = wait
        self.driver = driver

    async def get(self, url: str):
        await self.connection.request(
            url='/url',
            method='POST',
            data={
                'url': self.bind + url
            }
        )

    async def get_url(self):
        return await self.connection.request(
            url='/url',
            method='GET'
        )

    async def get_page_source(self) -> str:
        return await self.connection.request(
            url='/source',
            method='GET'
        )

    async def get_element(self, selector: str) -> Element:
        element_id = await self.connection.request(
            url='/element',
            method='POST',
            data={
                'using': 'css selector',
                'value': selector
            }
        )
        return self.create_element(element_id)

    async def get_elements(self, selector: str) -> List[Element]:
        result = await self.connection.request(
            url='/elements',
            method='POST',
            data={
                'using': 'css selector',
                'value': selector
            }
        )
        return [self.create_element(element_id) for element_id in result]

    async def wait_for_element(self, timeout: int, selector: str) -> Element:
        return await self.wait(
            timeout,
            partial(self.get_element, selector),
            NoSuchElement
        )

    async def wait_for_element_gone(self, timeout: int, selector: str):
        async def callback():
            try:
                await self.get_element(selector)
            except NoSuchElement:
                return True
            else:
                return False
        return await self.wait(timeout, callback)

    async def add_cookie(self, name: str, value: str, *, path: str=UNSET, domain: str=UNSET, secure: bool=UNSET, expiry: int=UNSET):
        cookie = {
            'name': name,
            'value': value
        }
        if path is not UNSET:
            cookie['path'] = path
        if domain is not UNSET:
            cookie['domain'] = domain
        if secure is not UNSET:
            cookie['secure'] = secure
        if expiry is not UNSET:
            cookie['expiry'] = expiry
        await self.connection.request(
            url='/cookie',
            method='POST',
            data={
                'cookie': cookie
            }
        )

    async def get_cookie(self, name: str):
        return await self.connection.request(
            url=f'/cookie/{name}',
            method='GET'
        )

    async def get_all_cookies(self):
        return await self.connection.request(
            url='/cookie',
            method='GET'
        )

    async def delete_cookie(self, name: str):
        await self.connection.request(
            url=f'/cookie/{name}',
            method='DELETE'
        )

    async def delete_all_cookies(self):
        await self.connection.request(
            url='/cookie',
            method='DELETE'
        )

    async def execute_script(self, script: str, *args: Any):
        return await self.connection.request(
            url='/execute/sync',
            method='POST',
            data={
                'script': script,
                'args': list(args)
            }
        )

    async def set_window_size(self, width: int, height: int, handle: str='current'):
        return await self.connection.request(
            url='/window/rect',
            method='POST',
            data={
                'width': width,
                'height': height,
                'windowHandle': handle,
            }
        )

    async def get_window_size(self, handle: str='current') -> Tuple[int, int]:
        return await self.connection.request(
            url='/window/rect',
            method='GET',
            data={
                'windowHandle': handle,
            }
        )

    async def get_alert_text(self) -> str:
        return await self.connection.request(
            url='/alert/text',
            method='GET'
        )

    async def send_alert_text(self, value: str):
        return await self.connection.request(
            url='/alert/text',
            method='POST',
            data={
                'text': value
            }
        )

    async def dismiss_alert(self):
        return await self.connection.request(
            url='/alert/dismiss',
            method='POST'
        )

    async def accept_alert(self):
        return await self.connection.request(
            url='/alert/accept',
            method='POST'
        )

    async def perform_actions(self, actions: Dict[str, Any]):
        return await self.connection.request(
            url='/actions',
            method='POST',
            data=actions
        )

    async def close(self):
        await self.connection.request(
            url='',
            method='DELETE'
        )

    def create_element(self, element_id):
        return self.element_class(
            element_id,
            self.connection.prefixed(f'/element/{element_id}'),
            self
        )


class CompatSession(Session):
    async def set_window_size(self, width: int, height: int,
                              handle: str = 'current'):
        return await self.connection.request(
            url=f'/window/{handle}/size',
            method='POST',
            data={
                'width': width,
                'height': height
            }
        )

    async def get_window_size(self, handle: str = 'current'):
        return await self.connection.request(
            url=f'/window/{handle}/size',
            method='GET'
        )

    async def execute_script(self, script, *args):
        return await self.connection.request(
            url='/execute',
            method='POST',
            data={
                'script': script,
                'args': list(args)
            }
        )

    async def perform_actions(self, actions: Dict[str, Any]):
        for url, method, data in transform_legacy_actions(actions['actions']):
            await self.connection.request(
                url=url,
                method=method,
                data=data,
            )


def _pointer_down(device, action):
    del action['duration']
    url = '/buttondown' if device['parameters']['pointerType'] == 'mouse' else '/touch/down'
    return url, 'POST', action


def _pointer_up(device, action):
    del action['duration']
    url = '/buttonup' if device['parameters']['pointerType'] == 'mouse' else '/touch/up'
    return url, 'POST', action


def _pointer_move(device, action):
    del action['duration']
    url = '/moveto' if device['parameters']['pointerType'] == 'mouse' else '/touch/move'
    origin = action['origin']
    if origin == 'pointer':
        data = {
            'xoffset': action['x'],
            'yoffset': action['y'],
        }
    elif WEB_ELEMENT in origin:
        data = {
            'element': origin[WEB_ELEMENT],
        }
    else:
        raise OperationNotSupported(f'Cannot move using origin {origin}')
    return url, 'POST', data


def _pause(device, action):
    return None


def key_down(device, action):
    return '/keydown', 'POST', {''}


legacy_actions = {
    ('pointer', 'pointerDown'): _pointer_down,
    ('pointer', 'pointerUp'): _pointer_up,
    ('pointer', 'pointerMove'): _pointer_move,
    ('pointer', 'pause'): _pause,
    ('key', 'pause'): _pause,
}


@attr.s
class LegacyAction:
    device = attr.ib()
    action = attr.ib()


def get_legacy_actions(devices: List[Dict[str, Any]]) -> Iterator[LegacyAction]:
    i = 0
    while devices:
        for device in devices:
            action = device['actions'].pop(0)
            i += 1
            yield LegacyAction(device, action)
        devices = [
            device for device in devices if device['actions']
        ]


def transform_legacy_actions(devices: List[Dict[str, Any]]) -> Iterator[Tuple[str, str, Dict[str, Any]]]:
    for legacy_action in get_legacy_actions(devices):
        device_type = legacy_action.device['type']
        action_type = legacy_action.action['type']
        device = {key: value for key, value in legacy_action.device.items() if key != 'type'}
        action = {key: value for key, value in legacy_action.action.items() if key != 'type'}
        try:
            handler = legacy_actions[(device_type, action_type)]
        except KeyError:
            raise OperationNotSupported(
                f'Unsupported action {action_type} for device_type {device_type}'
            )
        action = handler(device, action)
        if action is not None:
            yield action
