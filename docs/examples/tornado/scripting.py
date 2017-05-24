from tornado.ioloop import IOLoop

from arsenic.browsers import Firefox
from arsenic.engines.tornado import Tornado
from arsenic.services import Geckodriver


async def main():
    # Run geckodriver as a context manager using tornado
    async with Geckodriver().run(Tornado) as driver:
        # Request a Firefox session
        async with driver.session(Firefox()) as session:
            # Navigate to example.com
            await session.get('http://example.com')
            # Wait up to 10 seconds for the h1 to appear
            h1 = await session.wait_for_element(10, 'h1')
            # Return the text of the h1
            return await h1.get_text()


if __name__ == '__main__':
    title = IOLoop.instance().run_sync(main)
    print(f'The Title is: {title}')
