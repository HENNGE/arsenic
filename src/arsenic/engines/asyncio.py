import asyncio
import os
from asyncio.subprocess import Process, DEVNULL
from typing import TextIO, Dict, List

import attr


@attr.s
class ProcessContext:
    process = attr.ib()

    async def close(self):
        self.process.terminate()
        try:
            asyncio.wait_for(self.process.communicate(), 1)
        except TimeoutError:
            self.process.kill()
        try:
            asyncio.wait_for(self.process.communicate(), 1)
        except TimeoutError:
            pass


async def start_process(cmd: List[str], env: Dict[str, str], log: TextIO) -> ProcessContext:
    if log is os.devnull:
        log = DEVNULL
    process = await asyncio.create_subprocess_exec(
        *cmd,
        env=env,
        stdout=log,
        stderr=log,
    )
    return ProcessContext(process)
