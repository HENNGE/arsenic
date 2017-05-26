import base64
import json
from io import BytesIO
from json import JSONDecodeError
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from structlog import get_logger

from arsenic import errors
from arsenic.engines import Request, Response, HTTPSession


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


class Connection:
    def __init__(self, session: HTTPSession, prefix: str):
        self.session = session
        self.prefix = prefix

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
        try:
            data = json.loads(response.body)
        except JSONDecodeError as exc:
            log.error('json-decode', body=response.body)
            data = {
                'error': '!internal',
                'message': str(exc),
                'stacktrace': ''
            }
        wrap_screen(data)
        log.info('response', request=request, response=response, data=data)
        errors.check_response(response.status, data)
        if raw:
            return data
        if data:
            return unwrap(data.get('value', None))

    async def upload_file(self, path: Path) -> Path:
        log.info('upload-file', path=path, resolved_path=path)
        return path

    def prefixed(self, prefix: str) -> 'Connection':
        return self.__class__(self.session, self.prefix + prefix)


class RemoteConnection(Connection):
    async def upload_file(self, path: Path) -> Path:
        fobj = BytesIO()
        with ZipFile(fobj, 'w', ZIP_DEFLATED) as zf:
            zf.write(path, path.name)
        content = base64.b64encode(fobj.getvalue()).decode('utf-8')
        resolved = await self.request(
            url='/file',
            method='POST',
            data={
                'file': content
            }
        )
        log.info('upload-file', path=path, resolved_path=resolved)
        return resolved
