import abc
import base64
from typing import Dict, TypeVar, Union, Optional

import attr


TDefault = TypeVar('TDefault')


def lowercase_dict(data: Dict[str, str]) -> Dict[str, str]:
    return {key.lower(): value for key, value in data.items()}


@attr.s
class Headers:
    data: Dict[str, str] = attr.ib(convert=lowercase_dict, default=attr.Factory(dict))

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
    headers: Headers = attr.ib()
    body: bytes = attr.ib(repr=False)


class HTTPSession(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def request(self, request: Request) -> Response:
        raise NotImplementedError()

    @abc.abstractmethod
    async def close(self):
        raise NotImplementedError()


@attr.s
class Engine:
    http_session: HTTPSession = attr.ib()
    start_process = attr.ib()
    sleep = attr.ib()


class Auth(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_headers(self) -> Dict[str, str]:
        raise NotImplementedError()


@attr.s
class BasicAuth(Auth):
    username = attr.ib()
    password = attr.ib()

    def get_headers(self):
        raw_token = f'{self.username}:{self.password}'
        token = base64.b64encode(raw_token.encode('ascii')).decode('ascii')
        return {
            'Authorization': f'Basic {token}'
        }
