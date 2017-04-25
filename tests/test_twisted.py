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
def test_get_page_source():
    port = reactor.listenTCP(0, Site(Index())).getHost().port
    driver = yield drivers.init(drivers.ChromeDriver, TwistedClient)
    try:
        yield driver.get(f'http://127.0.0.1:{port}/')
        source = yield driver.get_page_source()
        assert 'Hello Twisted!' in source
    finally:
        yield driver.quit()
