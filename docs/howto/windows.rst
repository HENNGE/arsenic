Arsenic on Windows
##################

Use ``ProactorEventLoop``
*************************

Unless you're using the :py:class:`arsenic.services.Remote` service, you have to
use the :py:class:`asyncio.ProactorEventLoop` event loop to run arsenic. See
the `Python documentation`_ for more information.


Explicitly specify binaries
***************************

On unix systems, local services will work out of the box. On Windows, you need
to explicitly pass the absolute path to the services binary to the service.

For example, if you installed ``geckodriver.exe`` to ``C:\geckodriver\geckodriver.exe``,
you have to instantiate your arsenic session like this::

    from arsenic import get_session, services, browsers

    async def example():
        service = services.Geckodriver(
            binary='C:\\geckodriver\\geckodriver.exe'
        )
        browser = browsers.Firefox()
        async with get_session(service, browser) as session:
            ...


.. _Python documentation: https://docs.python.org/3/library/asyncio-eventloops.html#asyncio.ProactorEventLoop
