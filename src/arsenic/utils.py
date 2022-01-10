import socket
from typing import Union

import attr


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("0.0.0.0", 0))
        sock.listen(5)
        return sock.getsockname()[1]


def px_to_number(value: str) -> Union[int, float]:
    original = value
    if value.endswith("px"):
        value = value[:-2]
    if value.isdigit():
        return int(value)
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"{original!r} is not an number or <number>px value")


@attr.s
class Rect:
    x: float = attr.ib()
    y: float = attr.ib()
    width: float = attr.ib()
    height: float = attr.ib()
