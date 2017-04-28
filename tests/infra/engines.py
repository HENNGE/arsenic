import asyncio
from functools import partial

import attr
from tornado.ioloop import IOLoop

from arsenic.engines.aiohttp import Aiohttp
from arsenic.engines.tornado import Tornado


@attr.s
class LoopContext:
    loop = attr.ib()
    run = attr.ib()
    stop = attr.ib()


def start_aiohttp_loop():
    policy = asyncio.get_event_loop_policy()
    old_loop = policy.get_event_loop()
    loop = policy.new_event_loop()
    policy.set_event_loop(loop)
    loop = asyncio.get_event_loop_policy().new_event_loop()

    def run(func, *args, **kwargs):
        return loop.run_until_complete(asyncio.wait_for(func(*args, **kwargs), 15))

    def stop():
        policy.set_event_loop(old_loop)

    return LoopContext(
        loop,
        run,
        stop
    )


def start_tornado_loop():
    loop = IOLoop(make_current=True)

    def run(func, *args, **kwargs):
        return loop.run_sync(partial(func, *args, **kwargs), timeout=15)

    def stop():
        loop.clear_current()
        if not IOLoop.initialized() or loop is not IOLoop.instance():
            loop.close(all_fds=True)

    return LoopContext(
        loop,
        run,
        stop
    )


@attr.s
class EngineContext:
    start_loop = attr.ib()
    engine = attr.ib()
    name = attr.ib()


ENGINE_CONTEXTS = [
    EngineContext(
        start_loop=start_aiohttp_loop,
        engine=Aiohttp,
        name='aiohttp'
    ),
    EngineContext(
        start_loop=start_tornado_loop,
        engine=Tornado,
        name='tornado'
    )
]
