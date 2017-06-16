import asyncio
import base64
import json
from functools import wraps
from io import BytesIO
from json import JSONDecodeError
from pathlib import Path
from typing import Any
from zipfile import ZipFile, ZIP_DEFLATED

from aiohttp import ClientSession, ClientResponse
from structlog import get_logger

from arsenic import errors


WEB_ELEMENT = 'element-6066-11e4-a52e-4f735466cecf'


log = get_logger()


def unwrap(value):
    """
    Unwrap a value returned from a webdriver. Specifically this means trying to
    extract the element ID of a web element or a list of web elements.
    """
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
    """
    Data returned from a webdriver may contain a screen, which is a base64
    encoded PNG of the browser screen. This is a massive string and will make
    logging useless, so we wrap it in a BytesIO.
    """
    if isinstance(data, dict) and 'value' in data and isinstance(data['value'], dict) and 'screen' in data['value'] and data['value']['screen']:
        data['value']['screen'] = BytesIO(base64.b64decode(data['value']['screen']))


def ensure_task(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.get_event_loop().create_task(func(*args, **kwargs))
    return wrapper


class Connection:
    def __init__(self, session: ClientSession, prefix: str):
        self.session = session
        self.prefix = prefix

    @ensure_task
    async def request(self, *, url: str, method: str, data=None, raw=False):
        if data is None:
            data = {}
        if method not in {'POST', 'PUT'}:
            data = None
        body = json.dumps(data) if data is not None else None
        full_url = self.prefix + url
        log.info('request', url=full_url, method=method, body=body)
        response: ClientResponse = await self.session.request(
            url=full_url,
            method=method,
            data=body
        )
        response_body = await response.read()
        try:
            data = json.loads(response_body)
        except JSONDecodeError as exc:
            log.error('json-decode', body=response_body)
            data = {
                'error': '!internal',
                'message': str(exc),
                'stacktrace': ''
            }
        wrap_screen(data)
        log.info('response', url=full_url, method=method, body=body, response=response, data=data)
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
