# Async Webdriver

[![CircleCI](https://circleci.com/gh/HDE/arsenic/tree/main.svg?style=svg)](https://circleci.com/gh/HDE/arsenic/tree/main) [![Documentation Status](https://readthedocs.org/projects/arsenic/badge/?version=latest)](http://arsenic.readthedocs.io/en/latest/?badge=latest)
[![BrowserStack Status](https://automate.browserstack.com/badge.svg?badge_key=QmtNVHFnWWRFSEVUdTBZNWU5NGMraVorWVltazFqRk1VNWRydW5FRXU2dz0tLVhoTlFuK2tZUTJ1UGx0UmZaWjg4R1E9PQ==--35ef3d28fbf8ea24ee7fa2a435f9271fbaaf85d4)](https://automate.browserstack.com/public-build/QmtNVHFnWWRFSEVUdTBZNWU5NGMraVorWVltazFqRk1VNWRydW5FRXU2dz0tLVhoTlFuK2tZUTJ1UGx0UmZaWjg4R1E9PQ==--35ef3d28fbf8ea24ee7fa2a435f9271fbaaf85d4)
[![Appveyor status](https://ci.appveyor.com/api/projects/status/8l0koom7h93y1f9q?svg=true)](https://ci.appveyor.com/project/ojii/arsenic)
[![PyPI version](https://badge.fury.io/py/arsenic.svg)](https://badge.fury.io/py/arsenic)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


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

## CI Supported by Browserstack

Continuous integration for certain browsers is generously provided by [Browserstack](http://browserstack.com).

[![Browserstack](./.circleci/browserstack-logo.png)](http://browserstack.com/)
