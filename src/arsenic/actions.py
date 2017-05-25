import abc
from enum import Enum
from typing import List, Dict, Any, Union

import attr

from arsenic.connection import WEB_ELEMENT
from arsenic.session import Element


TOrigin = Union[Element, 'Origins']


class Origins(Enum):
    viewport = 'viewport'
    pointer = 'pointer'


class Button(Enum):
    left = 0
    middle = 1
    right = 2


class Device(metaclass=abc.ABCMeta):
    id: str = abc.abstractproperty()
    type: str = abc.abstractproperty()
    parameters: Dict[str, str] = abc.abstractproperty()

    def __init__(self):
        self.actions: List[Action] = []

    @abc.abstractmethod
    def encode_actions(self) -> List[Dict[str, Any]]:
        raise NotImplementedError()


@attr.s
class Action:
    type = attr.ib()
    duration = attr.ib()
    data = attr.ib()

    def encode(self):
        return {
            'type': self.type,
            'duration': self.duration,
            **self.data
        }


def encode_origin(origin):
    if isinstance(origin, Element):
        return {WEB_ELEMENT: origin.id}
    elif isinstance(origin, Origins):
        return origin.value
    else:
        raise TypeError()


class Mouse(Device):
    id = 'mouse'
    type = 'pointer'
    parameters = {
        'pointerType': 'mouse'
    }

    def move(self, origin: TOrigin, x: int, y: int, duration: int=250):
        self.actions.append(Action(
            type='pointerMove',
            duration=duration,
            data={
                'origin': encode_origin(origin),
                'x': x,
                'y': y
            }
        ))

    def button_down(self, button: Button=Button.left):
        self.actions.append(Action(
            type='pointerDown',
            duration=0,
            data={
                'button': button.value
            }
        ))

    def button_up(self, button: Button=Button.left):
        self.actions.append(Action(
            type='pointerUp',
            duration=0,
            data={
                'button': button.value
            }
        ))

    def encode_actions(self):
        return [action.encode() for action in self.actions]


class Actions:
    def __init__(self):
        self.mouse = Mouse()
        self.devices: List[Device] = [self.mouse]

    def move_to(self, element: Element) -> 'Actions':
        self.mouse.move(element, 0, 0)
        return self

    def move_by(self, x: int, y: int) -> 'Actions':
        self.mouse.move(Origins.pointer, x, y)
        return self

    def mouse_down(self) -> 'Actions':
        self.mouse.button_down()
        return self

    def mouse_up(self) -> 'Actions':
        self.mouse.button_up()
        return self

    def encode(self):
        return {
            'actions': [
                {
                    'id': device.id,
                    'type': device.type,
                    'parameters': device.parameters,
                    'actions': device.encode_actions(),
                } for device in self.devices
            ]
        }
