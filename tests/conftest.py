import asyncio
import sys

import pytest

pytest_plugins = [
    'tests.plugins.app.plugin',
    'tests.plugins.infra.plugin',
]

if sys.platform == 'win32':
    @pytest.fixture
    def event_loop():
        loop = asyncio.ProactorEventLoop()
        try:
            yield loop
        finally:
            loop.close()
