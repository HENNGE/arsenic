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
   * - Firefox
     - 54.0
     - Geckodriver 0.16.1
   * - PhantomJS
     - 1.9.8
     - PhantomJS 1.9.8
   * - Google Chrome
     - 59
     - Chromedriver 2.321


Headless Google Chrome
**********************


To use Google Chrome headless, use::

    service = services.Chromedriver()
    browser = browsers.Chrome(chromeOptions={
        'args': ['--headless', '--disable-gpu']
    })
    async with get_session(service, browser) as session:
        ...


Headless Firefox
****************

To use Firefox headless, use::

    service = services.Geckodriver()
    browser = browsers.Firefox(firefoxOptions={
        'args': ['-headless']
    })
    async with get_session(service, browser) as session:
        ...
