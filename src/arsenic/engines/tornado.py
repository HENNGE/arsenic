import os
from subprocess import DEVNULL
from typing import TextIO, Dict, List, Optional

import attr
from tornado.gen import sleep
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from tornado.ioloop import IOLoop
from tornado.process import Subprocess

from arsenic.engines import (
    Request, Response, Engine, Headers, HTTPSession,
    Auth,
)


def convert(headers):
    return Headers(dict(headers.get_all()))


class Session(HTTPSession):
    def __init__(self, client: AsyncHTTPClient, auth: Optional[Auth]=None):
        self.client = client
        self.auth = auth

    async def request(self, request: Request) -> Response:
        headers = {**request.headers}
        if self.auth is not None:
            headers.update(**self.auth.get_headers())
        try:
            response = await self.client.fetch(HTTPRequest(
                method=request.method,
                url=request.url,
                body=request.body,
                headers=headers,
            ))
        except HTTPError as exc:
            return Response(
                status=exc.code,
                body=exc.response.body if exc.response else exc.message,
                headers=convert(exc.response.headers) if exc.response else Headers(),
            )
        return Response(
            status=response.code,
            body=response.body,
            headers=convert(response.headers),
        )

    async def close(self):
        self.client.close()


@attr.s
class ProcessContext:
    process = attr.ib()

    async def close(self):
        self.process.proc.terminate()
        io_loop = IOLoop.current()
        def kill():
            try:
                self.process.proc.kill()
            except ProcessLookupError:
                pass
        handle = io_loop.call_later(1, kill)
        await self.process.wait_for_exit(False)
        io_loop.remove_timeout(handle)
        self.process = None
        Subprocess.uninitialize()


async def init_session(auth=None):
    return Session(AsyncHTTPClient(force_instance=True), auth)


async def start_process(cmd: List[str], env: Dict[str, str], log: TextIO) -> ProcessContext:
    if log is os.devnull:
        log = DEVNULL
    return ProcessContext(Subprocess(cmd, stdout=log, stderr=log, env=env))


Tornado = Engine(
    http_session=init_session,
    start_process=start_process,
    sleep=sleep
)
