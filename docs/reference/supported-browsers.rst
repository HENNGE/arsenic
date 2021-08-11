Supported Browsers
##################

.. note::

    A Browser is considered supported if it is tested in continuous integration.
    Other browsers and browser versions might also work, but are not tested.


.. list-table:: Browsers
   :header-rows: 1

   * - Browser Name
     - Supported Versions
     - Supported Service
     - OS
   * - Firefox
     - 59
     - Geckodriver 0.20.0
     - Linux, macOS, Windows 10
   * - Google Chrome
     - 65
     - Chromedriver 2.37
     - Linux, macOS, Windows 10
   * - Internet Explorer
     - 11 (See :ref:`ie11`)
     - IEDriverServer
     - Windows 10

Remote sessions are available via the :py:class:`arsenic.services.Remote` but not all APIs may be available.


Headless Google Chrome
**********************


To use Google Chrome headless, use::

    service = services.Chromedriver()
    browser = browsers.Chrome(chromeOptions={
        'args': ['--headless', '--disable-gpu']
    })
    async with get_session(service, browser) as session:
        ...


Google Chrome Device Emulation
******************************

To enable device emulation mode with Google Chrome, you can use::

    from arsenic import services, browsers, get_session

    service = services.Chromedriver()

    device_metrics = dict(width=640, height=480, pixelRatio=1.0)

    mobile_emulation = dict(deviceMetrics=device_metrics)

    kwargs = {'goog:chromeOptions': dict(mobileEmulation=mobile_emulation)}

    browser = browsers.Chrome(**kwargs)

    async with get_session(service, browser) as session:
        ...


Google Chrome Device Emulation And Headless
*******************************************

To enable device emulation mode and headless mode at the same time with Google Chrome, you can use::


    from arsenic import services, browsers

    service = services.Chromedriver(binary='chromedriver')

    device_metrics = dict(width=640, height=480, pixelRatio=1.0)

    mobile_emulation = dict(deviceMetrics=device_metrics)

    args=['--headless', '--disable-gpu']
    kwargs = {'goog:chromeOptions': dict(mobileEmulation=mobile_emulation, args=args)}

    browser = browsers.Chrome(**kwargs)

    async with get_session(service, browser) as session:
        ...


Headless Firefox
****************

To use Firefox headless, use::

    service = services.Geckodriver()
    browser = browsers.Firefox(**{"moz:firefoxOptions": {
        'args': ['-headless']
    }})
    async with get_session(service, browser) as session:
        ...
