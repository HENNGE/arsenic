from operator import itemgetter

from arsenic.actions import Mouse, Touch, chain
from arsenic.connection import WEB_ELEMENT
from arsenic.session import Element


ELEMENT_ONE = Element('1', None, None)
ELEMENT_TWO = Element('2', None, None)
ELEMENT_TRI = Element('3', None, None)


def test_drag_n_drop():
    mouse = Mouse()
    actions = chain(
        mouse.move_to(ELEMENT_ONE),
        mouse.down(),
        mouse.move_by(100, 100),
        mouse.up()
    )
    assert actions == {
        'actions': [
            {
                'parameters': {
                    'pointerType': 'mouse'
                },
                'id': 'pointer1',
                'type': 'pointer',
                'actions': [
                    {
                        'type': 'pointerMove',
                        'duration': 250,
                        'origin': {
                            WEB_ELEMENT: '1'
                        },
                        'x': 0,
                        'y': 0
                    },
                    {
                        'type': 'pointerDown',
                        'duration': 0,
                        'button': 0
                    },
                    {
                        'type': 'pointerMove',
                        'duration': 250,
                        'origin': 'pointer',
                        'x': 100,
                        'y': 100
                    },
                    {
                        'type': 'pointerUp',
                        'duration': 0,
                        'button': 0
                    }
                ]
            }
        ]
    }


def test_two_finger():
    finger1 = Touch()
    finger2 = Touch()
    actions = chain(
        finger1.move_to(ELEMENT_ONE) & finger2.move_to(ELEMENT_TWO),
        finger1.down() & finger2.down(),
        finger2.move_to(ELEMENT_TRI),
        finger1.up() & finger2.up()
    )
    devices = list(sorted(actions['actions'], key=itemgetter('id')))
    assert devices == [
        {
            'parameters': {
                'pointerType': 'touch'
            },
            'id': 'pointer1',
            'type': 'pointer',
            'actions': [
                {
                    'type': 'pointerMove',
                    'duration': 250,
                    'origin': {
                        WEB_ELEMENT: '1'
                    },
                    'x': 0,
                    'y': 0
                },
                {
                    'type': 'pointerDown',
                    'duration': 0,
                    'button': 0,
                },
                # create implicitly
                {
                    'type': 'pause',
                    'duration': 0
                }, {
                    'type': 'pointerUp',
                    'duration': 0,
                    'button': 0,
                }
            ]
        },
        {
            'parameters': {
                'pointerType': 'touch'
            },
            'id': 'pointer2',
            'type': 'pointer',
            'actions': [
                {
                    'type': 'pointerMove',
                    'duration': 250,
                    'origin': {
                        WEB_ELEMENT: '2'
                    },
                    'x': 0,
                    'y': 0
                },
                {
                    'type': 'pointerDown',
                    'duration': 0,
                    'button': 0,
                }, {
                    'type': 'pointerMove',
                    'duration': 250,
                    'origin': {
                        WEB_ELEMENT: '3'
                    },
                    'x': 0,
                    'y': 0
                }, {
                    'type': 'pointerUp',
                    'duration': 0,
                    'button': 0,
                }
            ]
        },
    ]
