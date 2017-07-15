import socket

import attr


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('0.0.0.0', 0))
        sock.listen(5)
        return sock.getsockname()[1]


def px_to_int(value: str) -> int:
    original = value
    if value.endswith('px'):
        value = value[:-2]
    if value.isdigit():
        return int(value)
    else:
        raise ValueError(f'{original!r} is not an int or <int>px value')


@attr.s
class Rect:
    x: float = attr.ib()
    y: float = attr.ib()
    width: float = attr.ib()
    height: float = attr.ib()
