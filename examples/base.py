from arsenic import drivers


async def run_selenium(port, client):
    async with drivers.context(drivers.ChromeDriver, client) as driver:
        await driver.get(f'http://127.0.0.1:{port}/')
        return await driver.get_page_source()
