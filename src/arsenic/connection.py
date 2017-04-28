import json
from json import JSONDecodeError

import attr

from arsenic import errors
from arsenic.engines import Request, Response

WEB_ELEMENT = 'element-6066-11e4-a52e-4f735466cecf'


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
        response: Response = await self.session.request(request)
        try:
            data = json.loads(response.body)
        except JSONDecodeError as exc:
            data = {
                'error': '!internal',
                'message': str(exc)
            }
        if 'error' in data or response.status != 200:
            error = errors.get(data.get('error', '!unkown'))
            raise error(data.get('message', data))
        if raw:
            return data
        if data:
            return unwrap(data.get('value', None))

    def prefixed(self, prefix: str) -> 'Connection':
        return Connection(self.session, self.prefix + prefix)
