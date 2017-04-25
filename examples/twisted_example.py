from twisted.internet import reactor
from twisted.internet.defer import ensureDeferred
from twisted.web.resource import Resource
from twisted.web.server import Site

from arsenic.clients.twisted import TwistedClient
import base


async def run_selenium(port):
    print('Hello Twisted!' in await base.run_selenium(port, TwistedClient))


# Simple Twisted app
class Index(Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader('Content-Type', 'text/plain')
        request.finish('Hello Twisted!')


def build_app():
    return Site(Index())


async def run():
    app = build_app()
    print('listening to port')
    port = reactor.listenTCP(0, app).getHost().port
    print('running selenium')
    await run_selenium(port)
    print('done')


def main():
    d = ensureDeferred(run())
    d.addBoth(reactor.stop)
    print('calling reactor.run()')
    reactor.run()


if __name__ == '__main__':
    main()
