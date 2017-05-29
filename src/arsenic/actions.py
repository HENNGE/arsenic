import abc
from enum import Enum
from typing import Sequence, Any, Iterator, List, Dict, Optional

import attr

from arsenic.connection import WEB_ELEMENT
from arsenic.session import Element


@attr.s
class Action:
    source = attr.ib()
    payload = attr.ib()


class Tick:
    def __init__(self, *actions: Action):
        self.actions: Dict['Device', 'Action'] = {
            action.source: action
            for action in actions
        }

    def __and__(self, other: 'Tick') -> 'Tick':
        overlap = set(self.actions.keys()) & set(other.actions.keys())
        if overlap:
            raise ValueError(
                f'Devices {overlap} have more than one action in this tick'
            )
        return Tick(*self.actions.values(), *other.actions.values())

    def encode(self, device: 'Device') -> Dict[str, Any]:
        if device not in self.actions:
            return {
                'type': 'pause',
                'duration': 0,
            }
        else:
            return self.actions[device].payload


class DeviceType(Enum):
    keyboard = 'key'
    pointer = 'pointer'


class PointerType(Enum):
    mouse = 'mouse'
    pen = 'pen'
    touch = 'touch'


class Button(Enum):
    left = 0
    middle = 1
    right = 2


class Device(metaclass=abc.ABCMeta):
    type: DeviceType = abc.abstractproperty()

    def __init__(self, device_id: Optional[str]=None):
        self.device_id = device_id

    def info(self, index: int) -> Dict[str, Any]:
        device_id = self.device_id or f'{self.type.value}{index}'
        return {
            'id': device_id,
            'type': self.type.value,
        }

    def _tick(self, **payload: Any) -> Tick:
        return Tick(Action(self, payload))

    def pause(self, duration: int) -> Tick:
        return self._tick(
            type='pause',
            duration=duration,
        )


class Pointer(Device, metaclass=abc.ABCMeta):
    type = DeviceType.pointer
    pointer_type: PointerType = abc.abstractproperty()

    def info(self, index: int) -> Dict[str, Any]:
        return {
            'parameters': {'pointerType': self.pointer_type.value},
            **super().info(index)
        }

    def move_to(self, element: Element, duration: int=250) -> Tick:
        return self._tick(
            type='pointerMove',
            duration=duration,
            origin={WEB_ELEMENT: element.id},
            x=0,
            y=0,
        )

    def move_by(self, x: int, y: int, duration: int=250) -> Tick:
        return self._tick(
            type='pointerMove',
            duration=duration,
            origin='pointer',
            x=x,
            y=y,
        )

    def down(self) -> Tick:
        return self._tick(
            type='pointerDown',
            duration=0,
            button=0,
        )

    def up(self) -> Tick:
        return self._tick(
            type='pointerUp',
            duration=0,
            button=0,
        )


class Mouse(Pointer):
    pointer_type = PointerType.mouse

    def down(self, button: Button=Button.left) -> Tick:
        return self._tick(
            type='pointerDown',
            duration=0,
            button=button.value
        )

    def up(self, button: Button=Button.left) -> Tick:
        return self._tick(
            type='pointerUp',
            duration=0,
            button=button.value
        )


class Pen(Pointer):
    pointer_type = PointerType.pen


class Touch(Pointer):
    pointer_type = PointerType.touch


class Keyboard(Device):
    type = DeviceType.keyboard

    def down(self, key: str) -> Tick:
        return self._tick(
            type='keyDown',
            value=key
        )

    def up(self, key: str) -> Tick:
        return self._tick(
            type='keyUp',
            value=key
        )


def gather_devices(ticks: Sequence[Tick]) -> Iterator[Device]:
    found = set()
    for tick in ticks:
        devices = set(tick.actions.keys())
        for device in devices - found:
            yield device
        found.update(devices)


def chain(*ticks: Tick) -> Dict[str, List[Dict[str, Any]]]:
    devices = list(gather_devices(ticks))
    return {
        'actions': [
            {
                **device.info(index),
                'actions': [tick.encode(device) for tick in ticks],
            } for index, device in enumerate(devices, start=1)
        ]
    }
