async def test_get_page_source(context):
    async with context.driver.run(context.engine) as driver:
        async with driver.session(context.browser, context.base_url) as session:
            await session.get('/')
            assert 'Hello World!' in await session.get_page_source()


async def test_simple_form_submit(context):
    async with context.driver.run(context.engine) as driver:
        async with driver.session(context.browser, context.base_url) as session:
            await session.get('/html/')
            field = await driver.wait(5, session.get_element, 'input[name="field"]')
            await field.send_keys('sample input')
            submit = await session.get_element('input[type="submit"]')
            await submit.click()
            h2 = await driver.wait(5, session.get_element, 'h2')
            assert 'sample input' == await h2.get_text()


async def test_displayed(context):
    async with context.driver.run(context.engine) as driver:
        async with driver.session(context.browser, context.base_url) as session:
            await session.get('/js/')
            button = await driver.wait(5, session.get_element, 'button')
            div = await driver.wait(5, session.get_element, '#secret')
            assert not await div.is_displayed()
            await button.click()
            assert await driver.wait(5, div.is_displayed)


async def test_execute_script(context):
    async with context.driver.run(context.engine) as driver:
        async with driver.session(context.browser, context.base_url) as session:
            await session.get('/js/')
            div = await driver.wait(5, session.get_element, 'div')
            assert not await div.is_displayed()
            await session.execute_script('document.getElementById("secret").removeAttribute("class");')
            assert await driver.wait(5, div.is_displayed)


async def test_cookies(context):
    async with context.driver.run(context.engine) as driver:
        async with driver.session(context.browser, context.base_url) as session:
            await session.get('/cookie/')
            h2 = await driver.wait(5, session.get_element, 'h2')
            assert '' == await h2.get_text()
            await session.add_cookie('test', 'value')
            await session.get('/cookie/')
            h2 = await driver.wait(5, session.get_element, 'h2')
            assert 'value' == await h2.get_text()
            await session.delete_cookie('test')
            await session.get('/cookie/')
            h2 = await driver.wait(5, session.get_element, 'h2')
            assert '' == await h2.get_text()
