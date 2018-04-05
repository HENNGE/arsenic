Arsenic on Windows
##################

.. _ie11:

Internet Explorer 11
********************

If you're trying to run Internet Explorer 11 using IEDriverServer, you must configure your
computer a certain way. A helper function :py:func:`arsenic.helpers.check_ie11_environment`
is provided and a helper script ``arsenic-check-ie11.exe`` can also be called from the command line.

To manually check the environment, ensure the following are all true:

* The *Protected Mode* setting of all zones in *Internet Options* must be set to the same value.
* *Enhanced Protected Mode* me *disabled*.
* The *Zoom Level* of Internet Explorer must be set to *100%*.
* The *Scale factor* in *Settings* -> *Display* must be set to *100*.

All of these, except for the *Scale factor* can be set with ``arsenic-configure-ie11.exe``. This will disable
*Protected Mode* for all zones! You may require elevated privileges to run this command.


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
