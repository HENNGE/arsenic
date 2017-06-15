import abc
import base64
from typing import Dict

import attr


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
