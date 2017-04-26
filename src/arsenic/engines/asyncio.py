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
        handle = asyncio.get_event_loop().call_later(5, self.process.kill)
        await self.process.wait()
        handle.cancel()


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
