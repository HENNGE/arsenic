# Async Webdriver

[![CircleCI](https://circleci.com/gh/HDE/arsenic/tree/master.svg?style=svg)](https://circleci.com/gh/HDE/arsenic/tree/master) [![Documentation Status](https://readthedocs.org/projects/arsenic/badge/?version=latest)](http://arsenic.readthedocs.io/en/latest/?badge=latest)


Asynchronous, framework-independent webdriver client for AsyncIO/Aiohttp and
Tornado.


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
            h1 = await driver.wait_for_element(5, 'h1')
            # print the text of the h1 element
            print(await h1.get_text())
```
