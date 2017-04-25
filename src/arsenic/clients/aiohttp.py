from asyncio import sleep

import async_timeout
from aiohttp.client import ClientSession

from . import Client, Request, Response, Headers
from .asyncio import start_process, terminate_process


async def init_session():
    return ClientSession()


async def close_session(session: ClientSession):
    session.close()


async def send_request(session: ClientSession, request: Request) -> Response:
    request_context = session.request(
        method=request.method,
        url=request.url,
        data=request.body,
        headers=request.headers
    )

    with async_timeout.timeout(10):
        async with request_context as response:
            body = await response.read()
            status = response.status
            headers = Headers(response.headers)
    return Response(
        status=status,
        body=body,
        headers=headers,
    )


AiohttpClient = Client(
    init_session=init_session,
    close_session=close_session,
    send_request=send_request,
    start_process=start_process,
    terminate_process=terminate_process,
    sleep=sleep,
)
