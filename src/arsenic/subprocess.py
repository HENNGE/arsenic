import abc
import asyncio
import os
import subprocess
import sys
from typing import List, TypeVar
from asyncio.subprocess import DEVNULL, PIPE

from structlog import get_logger

log = get_logger()


P = TypeVar("P")


def check_event_loop():
    if sys.platform == "win32" and isinstance(
        asyncio.get_event_loop(), asyncio.SelectorEventLoop
    ):
        raise ValueError(
            "SelectorEventLoop is not supported on Windows, use asyncio.ProactorEventLoop instead."
        )


class BaseSubprocessImpl(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def run_process(self, cmd: List[str]) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    async def start_process(self, cmd: List[str], log_file) -> P:
        pass

    @abc.abstractmethod
    async def stop_process(self, process: P) -> None:
        pass


class AsyncioSubprocessImpl(BaseSubprocessImpl):
    async def run_process(self, cmd: List[str]) -> str:
        check_event_loop()
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=PIPE, stderr=PIPE, stdin=DEVNULL
        )
        out, err = await process.communicate()
        if process.returncode != 0:
            raise Exception(err)
        else:
            return out.decode("utf-8")

    async def start_process(self, cmd: List[str], log_file):
        check_event_loop()
        if log_file is os.devnull:
            log_file = DEVNULL
        return await asyncio.create_subprocess_exec(
            *cmd, stdout=log_file, stderr=log_file, stdin=DEVNULL
        )

    async def stop_process(self, process):
        process.terminate()
        try:
            await asyncio.wait_for(process.communicate(), 1)
        except asyncio.futures.TimeoutError:
            process.kill()
        try:
            await asyncio.wait_for(process.communicate(), 1)
        except asyncio.futures.TimeoutError:
            log.warn("could not terminate process", process=process, impl=self)


class ThreadedSubprocessImpl(BaseSubprocessImpl):
    async def run_process(self, cmd: List[str]):
        return await asyncio.get_event_loop().run_in_executor(
            None, self._run_process, cmd
        )

    def _run_process(self, cmd):
        return subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL
        ).decode("utf-8")

    async def start_process(self, cmd: List[str], log_file):
        if log_file is os.devnull:
            log_file = subprocess.DEVNULL
        return await asyncio.get_event_loop().run_in_executor(
            None, self._start_process, cmd, log_file
        )

    def _start_process(self, cmd: List[str], log_file):
        return subprocess.Popen(
            cmd, stdout=log_file, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL
        )

    async def stop_process(self, process):
        return await asyncio.get_event_loop().run_in_executor(
            None, self._stop_process, process
        )

    def _stop_process(self, process: subprocess.Popen):
        process.terminate()
        try:
            process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()
        try:
            process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            log.warn("could not terminate process", process=process, impl=self)


def get_subprocess_impl() -> BaseSubprocessImpl:
    if sys.platform == "win32":
        if isinstance(asyncio.get_event_loop(), asyncio.SelectorEventLoop):
            return ThreadedSubprocessImpl()
        else:
            return AsyncioSubprocessImpl()
    else:
        return AsyncioSubprocessImpl()
