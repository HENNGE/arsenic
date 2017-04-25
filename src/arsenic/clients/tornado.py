import os
from subprocess import DEVNULL
from typing import TextIO, Dict, List

from tornado.gen import sleep
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.process import Subprocess

from . import Client, Request, Response, Headers


async def init_session():
    return AsyncHTTPClient()


async def close_session(session: AsyncHTTPClient):
    session.close()


async def send_request(session: AsyncHTTPClient, request: Request) -> Response:
    response = await session.fetch(HTTPRequest(
        method=request.method,
        url=request.url,
        body=request.body,
        headers=request.headers
    ))
    return Response(
        status=response.code,
        body=response.body,
        headers=Headers(dict(response.headers.get_all())),
    )


async def start_process(cmd: List[str], env: Dict[str, str], log: TextIO) -> Subprocess:
    if log is os.devnull:
        log = DEVNULL
    return Subprocess(cmd, stdout=log, stderr=log, env=env)


async def terminate_process(process: Subprocess):
    process.proc.terminate()
    await process.wait_for_exit(False)
    process.proc.kill()


TornadoClient = Client(
    init_session=init_session,
    close_session=close_session,
    send_request=send_request,
    start_process=start_process,
    terminate_process=terminate_process,
    sleep=sleep
)
