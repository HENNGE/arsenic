import base64
import json
from io import BytesIO
from json import JSONDecodeError

import attr
from structlog import get_logger

from arsenic import errors
from arsenic.engines import Request, Response

WEB_ELEMENT = 'element-6066-11e4-a52e-4f735466cecf'


log = get_logger()


def unwrap(value):
    if isinstance(value, dict) and ('ELEMENT' in value or WEB_ELEMENT in value):
        wrapped_id = value.get('ELEMENT', None)
        if wrapped_id:
            return value['ELEMENT']
        else:
            return value[WEB_ELEMENT]

    elif isinstance(value, list):
        return list(unwrap(item) for item in value)
    else:
        return value


def wrap_screen(data):
    if isinstance(data, dict) and 'value' in data and isinstance(data['value'], dict) and 'screen' in data['value']:
        data['value']['screen'] = BytesIO(base64.b64decode(data['value']['screen']))


@attr.s
class Connection:
    session = attr.ib()
    prefix: str = attr.ib()

    async def request(self, *, url: str, method: str, data=None, raw=False):
        if data is None:
            data = {}
        if method not in {'POST', 'PUT'}:
            data = None
        request = Request(
            url=self.prefix + url,
            method=method,
            body=json.dumps(data) if data is not None else None
        )
        log.info('request', request=request)
        response: Response = await self.session.request(request)
        log.info('response', request=request, response=response)
        try:
            data = json.loads(response.body)
        except JSONDecodeError as exc:
            data = {
                'error': '!internal',
                'message': str(exc)
            }
        wrap_screen(data)
        errors.check_response(data)
        if raw:
            return data
        if data:
            return unwrap(data.get('value', None))

    def prefixed(self, prefix: str) -> 'Connection':
        return Connection(self.session, self.prefix + prefix)
