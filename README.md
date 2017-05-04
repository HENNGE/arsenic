# Async Webdriver

[![CircleCI](https://circleci.com/gh/ojii/arsenic/tree/master.svg?style=svg)](https://circleci.com/gh/ojii/arsenic/tree/master)

Asynchronous, framework-independent webdriver client.

## Features

### Supported Frameworks

* Tornado Support
* Asyncio/Aiohttp Support

### Supported Browsers

* Firefox
* Remote Firefox

### Supported APIs

* Start/stop session
* Go to URL
* Get URL
* Get page source
* Find element
* Get element text
* Send keys to element
* Click element
* Wait (eg until an element is there)


## Quickstart

Let's run Firefox via Geckodriver using Aiohttp.


```python

from arsenic.engines.aiohttp import Aiohttp
from arsenic.browsers import Firefox
from arsenic.services import Geckodriver


async def example():
    # start geckodriver using aiohttp/asyncio
    async with Geckodriver().run(Aiohttp) as driver:
        # start a new browser session
        async with driver.session(Firefox()) as session:
            # go to example.com
            await session.get('http://example.com')
            # wait up to 5 seconds to get the h1 element from the page
            h1 = await driver.wait(5, session.get_element, 'h1')
            # print the text of the h1 element
            print(await h1.get_text())
```

## Testing

To run the tests, install circleci local and run `circleci build`.

Alternatively you can run the app in `tests/app/` manually, set
the `WEB_APP_BASE_URL` environment variable to the URL at which the
app is running and execute `pytest`.
