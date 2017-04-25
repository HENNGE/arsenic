from typing import TextIO, Dict, List

from twisted.internet import reactor
from twisted.internet.defer import Deferred, succeed
from twisted.internet.error import ProcessDone
from twisted.internet.protocol import Protocol, connectionDone, ProcessProtocol
from twisted.web.client import (
    Agent, Headers as TwistedHeaders,
    HTTPConnectionPool,
)

from . import Client, Request, Response, Headers


class SimpleProducer:
    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


class SimpleReceiver(Protocol):
    def __init__(self, deferred):
        self.buf = b''
        self.deferred = deferred

    def dataReceived(self, data):
        self.buf += data

    def connectionLost(self, reason=connectionDone):
        self.deferred.callback(self.buf)



async def init_session() -> Agent:
    print('init session')
    pool = HTTPConnectionPool(reactor, persistent=True)
    return Agent(reactor, pool=pool)


async def close_session(session: Agent):
    pass

async def send_request(session: Agent, request: Request) -> Response:
    print('send request')
    headers = TwistedHeaders()
    for key, value in request.headers.items():
        headers.addRawHeader(key, value)
    response = await session.request(
        method=request.method,
        uri=request.url,
        headers=headers,
        bodyProducer=SimpleProducer(request.body)
    )

    d = Deferred()
    response.deliverBody(SimpleReceiver(d))
    body = await d

    return Response(
        status=response.code,
        body=body,
        headers=Headers({
            key: values[0]
            for key, values in response.headers.getAllRawHeaders()
        })
    )


class SimpleProcessProtocol(ProcessProtocol):
    def __int__(self, log):
        self.log = log
        self.returncode = None
        
    def connectionMade(self):
        print('connectionMade')
        self.transport.closeStdin()

    def outReceived(self, data):
        print('outReceived', data)
        self.log.write(data)

    def errReceived(self, data):
        print('errReceived', data)
        self.log.write(data)

    def processExited(self, status):
        print('processExited', status)
        if isinstance(status.value, ProcessDone):
            self.returncode = 0
        else:
            self.returncode = status.value.exitCode

    def terminate(self):
        self.transport.signalProcess('KILL')
        self.transport.loseConnection()


async def start_process(cmd: List[str], env: Dict[str, str], log: TextIO) -> SimpleProcessProtocol:
    print('start process')
    protocol = SimpleProcessProtocol(log)
    reactor.spawnProcess(protocol, cmd[0], args=cmd, env=env)
    print('process spawned', protocol)
    return protocol


async def terminate_process(process: SimpleProcessProtocol):
    process.terminate()


def sleep(secs):
    d = Deferred()
    reactor.callLater(secs, d.callback, None)
    return d


TwistedClient = Client(
    init_session=init_session,
    close_session=close_session,
    send_request=send_request,
    start_process=start_process,
    terminate_process=terminate_process,
    sleep=sleep
)
