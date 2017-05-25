from functools import partial
from pathlib import Path
from typing import Awaitable, Callable, Any, List, TYPE_CHECKING

from arsenic.connection import Connection, WEB_ELEMENT
from arsenic.errors import NoSuchElement, OperationNotSupported

if TYPE_CHECKING:
    from arsenic.actions import Actions

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

    def __init__(self, connection: Connection, wait=TWaiter, bind: str=''):
        self.connection = connection
        self.bind = bind
        self.wait = wait

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

    async def get_page_source(self):
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

    async def add_cookie(self, name, value, *, path=UNSET, domain=UNSET, secure=UNSET, expiry=UNSET):
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

    async def get_cookie(self, name):
        return await self.connection.request(
            url=f'/cookie/{name}',
            method='GET'
        )

    async def get_all_cookies(self):
        return await self.connection.request(
            url='/cookie',
            method='GET'
        )

    async def delete_cookie(self, name):
        await self.connection.request(
            url=f'/cookie/{name}',
            method='DELETE'
        )

    async def delete_all_cookies(self):
        await self.connection.request(
            url='/cookie',
            method='DELETE'
        )

    async def execute_script(self, script, *args):
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

    async def get_window_size(self, handle: str='current'):
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

    async def perform_actions(self, actions: 'Actions'):
        return await self.connection.request(
            url='/actions',
            method='POST',
            data=actions.encode()
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

    async def _pointer_down(self, device, action):
        await self.connection.request(
            url='/buttondown',
            method='POST',
            data=action.data
        )

    async def _pointer_up(self, device, action):
        await self.connection.request(
            url='/buttonup',
            method='POST',
            data=action.data
        )

    async def _pointer_move(self, device, action):
        origin = action.data['origin']
        if origin == 'pointer':
            await self.connection.request(
                url='/moveto',
                method='POST',
                data={
                    'xoffset': action.data['x'],
                    'yoffset': action.data['y'],
                }
            )
        elif WEB_ELEMENT in origin:
            await self.connection.request(
                url='/moveto',
                method='POST',
                data={
                    'element': origin[WEB_ELEMENT],
                }
            )
        else:
            raise OperationNotSupported(f'Cannot move using origin {origin}')

    action_executors = {
        ('pointer', 'pointerDown'): _pointer_down,
        ('pointer', 'pointerUp'): _pointer_up,
        ('pointer', 'pointerMove'): _pointer_move
    }

    async def perform_actions(self, actions: 'Actions'):
        for device in actions.devices:
            for action in device.actions:
                key = (device.type, action.type)
                try:
                    executor = self.action_executors[key]
                except KeyError:
                    raise OperationNotSupported(
                        f'Action {action.type} of device type {device.type} is '
                        f'not supported by this session'
                    )
                await executor(self, device, action)
