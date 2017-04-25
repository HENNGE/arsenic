import asyncio
import os
from asyncio.subprocess import Process, DEVNULL
from typing import TextIO, Dict, List


async def start_process(cmd: List[str], env: Dict[str, str], log: TextIO) -> Process:
    if log is os.devnull:
        log = DEVNULL
    return await asyncio.create_subprocess_exec(
        *cmd,
        env=env,
        stdout=log,
        stderr=log,
    )


async def terminate_process(process: Process):
    process.terminate()
    await process.wait()
    process.kill()
