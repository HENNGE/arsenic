Extending
#########


Engine
******

An :ref:`Engine` must be an instance of :py:class:`arsenic.engines.Engine`. That class
requires three parameters: A coroutine which starts a new HTTP session, a
coroutine which starts a new subprocess and a coroutine which sleeps.

The coroutine to start a new HTTP session takes a single argument which is
either an instance of :py:class:`arsenic.engines.Auth` or :py:obj:`None`. It
must return an instance of :py:class:`arsenic.engines.HTTPSession` which must
implement two coroutine methods: :py:meth:`arsenic.engines.HTTPSession.request`
and :py:meth:`arsenic.engines.HTTPSession.close`

:py:meth:`arsenic.engines.HTTPSession.request` takes a single argument which is
an instance of :py:class:`arsenic.engines.Request` and must return a single
argument :py:class:`arsenic.engines.Response`.

:py:meth:`arsenic.engines.HTTPSession.close` takes no arguments and has no
return value and should close the session.

The coroutine to start the subprocess takes three arguments, a list of strings
which are the command to run, a dictionary where both the keys and values are
strings which are the environment variables to use for the subprocess and a
file object opened in text mode for writing to use for logging. It must return
an object which has a coroutine method named ``close`` which takes no arguments
and has no return value which stops the subprocess.

The sleep coroutine takes an integer or float as argument which is the number of
seconds the coroutine should sleep. It has no return value.

Dummy example
=============

.. code-block:: python3

    from typing import Optional, List, Dict, TextIO

    from arsenic.engines import Auth, HTTPSession, Request, Response, Headers, Engine

    from dummy import do_http_request, do_start_subprocess, do_sleep

    class DummyHTTPSession(HTTPSession):
        def __init__(self, auth):
            self.auth = auth

        async def request(self, request: Request) -> Response:
            headers = {
                **request.headers
            }
            if self.auth is not None:
                headers.update(self.auth.get_headers())

            status: int, body: bytes, headers: Headers = await do_http_request(
                method=request.method,
                url=request.url,
                data=request.body,
                headers=headers
            )

            return Response(
                status=status,
                body=body,
                headers=headers,
            )


    async def start_http_session(auth: Optional[Auth]=None):
        return DummyHTTPSession(auth)

    class SubprocessContext:
        def __init__(self, process):
            self.process = process

        async def close(self):
            await self.process.stop()

    async def start_subprocess(cmd: List[str], env: Dict[str, str], log: TextIO):
        return SubprocessContext(do_start_subprocess(cmd, env, log))

    DummyEngine = Engine(
        http_sesion=start_http_session,
        start_process=start_subprocess,
        sleep=do_sleep
    )


Service
*******

A :ref:`Service` must be a subclass of :py:class:`arsenic.service.Service` and implement
the :py:meth:`arsenic.service.Service.start` coroutine method. This method
takes an instance of an :py:class:`arsenic.engines.Engine` as argument and must
return an instance of :py:class:`arsenic.webdriver.WebDriver`.

If your service uses a local subprocess, the :py:func:`arsenic.service.subprocess_based_service`
helper might be useful.

Browser
*******

A :ref:`Browser` is an object with an attribute ``capabilities`` which is a JSON
serializable object that gets passed to the webdriver as the desired capabilities.

For convenience there is a :py:class:`arsenic.browsers.Browser` class you can
subclass and set the :py:attr:`arsenic.browsers.Browser.defaults` to a JSON
serializable dictionary of default values. The class can be passed a dictionary
of values to override when instantiated.

If your :ref:`Browser` does not support the web driver protocol, you can chose a
different :py:class:`arsenic.session.Session` class using the
:py:attr:`arsenic.browsers.Browser.session_class` attribute.
