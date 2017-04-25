import pytest
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site

from arsenic import drivers


# Simple Twisted app
from arsenic.clients.twisted import TwistedClient


class Index(Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader('Content-Type', 'text/plain')
        request.finish('Hello Twisted!')


@pytest.mark.xfail
@pytest.inlineCallbacks
async def test_get_page_source():
    port = reactor.listenTCP(0, Site(Index())).getHost().port
    async with drivers.context(drivers.ChromeDriver, TwistedClient) as driver:
        await driver.get(f'http://127.0.0.1:{port}/')
        assert 'Hello Twisted!' in await driver.get_page_source()
