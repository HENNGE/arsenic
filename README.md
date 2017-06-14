# Async Webdriver

[![CircleCI](https://circleci.com/gh/HDE/arsenic/tree/master.svg?style=svg)](https://circleci.com/gh/HDE/arsenic/tree/master) [![Documentation Status](https://readthedocs.org/projects/arsenic/badge/?version=latest)](http://arsenic.readthedocs.io/en/latest/?badge=latest)


Asynchronous webdriver client built on asyncio.


## Quickstart

Let's run a local Firefox instance.


```python

from arsenic import get_session
from arsenic.browsers import Firefox
from arsenic.services import Geckodriver


async def example():
    # Runs geckodriver and starts a firefox session
    async with get_session(Geckodriver(), Firefox()) as session:
          # go to example.com
          await session.get('http://example.com')
          # wait up to 5 seconds to get the h1 element from the page
          h1 = await session.wait_for_element(5, 'h1')
          # print the text of the h1 element
          print(await h1.get_text())
```

For more information, check [the documentation](https://arsenic.readthedocs.io/)
