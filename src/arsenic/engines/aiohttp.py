from asyncio import sleep
from typing import Optional

from aiohttp.client import ClientSession

from . import Engine, Request, Response, Headers, HTTPSession, Auth
from .asyncio import start_process


class Session(HTTPSession):
    def __init__(self, client: ClientSession, auth: Optional[Auth]=None):
        self.client = client
        self.auth = auth

    async def request(self, request: Request) -> Response:
        headers = {
            **request.headers
        }
        if self.auth is not None:
            headers.update(self.auth.get_headers())

        request_context = self.client.request(
            method=request.method,
            url=request.url,
            data=request.body,
            headers=headers
        )

        async with request_context as response:
            body = await response.read()
            status = response.status
            headers = Headers(response.headers)

        return Response(
            status=status,
            body=body,
            headers=headers,
        )

    async def close(self):
        await self.client.close()


async def init_session(auth=None):
    return Session(ClientSession(), auth)


Aiohttp = Engine(
    http_session=init_session,
    start_process=start_process,
    sleep=sleep,
)
