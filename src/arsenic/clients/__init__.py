from typing import (
    TypeVar, Dict, Optional, Union, Awaitable, Callable, List,
    TextIO,
)

import attr


TDefault = TypeVar('TDefault')


class Headers:
    def __init__(self, data: Dict[str, str]):
        self.data = {key.lower(): value for key, value in data.items()}

    def get(self, key: str, default: TDefault=None) -> Union[str, TDefault]:
        return self.data.get(key.lower(), default)


@attr.s
class Request:
    method: str = attr.ib()
    url: str = attr.ib()
    headers: Dict[str, str] = attr.ib(default=attr.Factory(lambda: {}))
    body: Optional[bytes] = attr.ib(default=None)


@attr.s
class Response:
    status: int = attr.ib()
    body: bytes = attr.ib()
    headers: Headers = attr.ib()


TSession = TypeVar('TSession')
TInitSession = Callable[[], Awaitable[TSession]]
TCloseSession = Callable[[TSession], Awaitable[None]]
TSendRequest = Callable[[TSession, Request], Awaitable[Response]]

TProcess = TypeVar('TProcess')
TStartProcess = Callable[[List[str], Dict[str, str], TextIO], Awaitable[TProcess]]
TProcessRunning = Callable[[TProcess], Awaitable[bool]]
TProcessReturnCode = Callable[[TProcess], Awaitable[int]]
TTerminateProcess = Callable[[TProcess], Awaitable[None]]

TSleeper = Callable[[int], Awaitable[None]]


async def get_return_code(process: TProcess) -> int:
    return process.returncode


async def process_running(process: TProcess) -> bool:
    return process.returncode is None


@attr.s
class Client:
    init_session: TInitSession = attr.ib()
    close_session: TCloseSession = attr.ib()
    send_request: TSendRequest = attr.ib()
    start_process: TStartProcess = attr.ib()
    terminate_process: TTerminateProcess = attr.ib()
    sleep: TSleeper = attr.ib()
    process_running: TProcessRunning = attr.ib(default=process_running)
    process_return_code: TProcessReturnCode = attr.ib(default=get_return_code)
