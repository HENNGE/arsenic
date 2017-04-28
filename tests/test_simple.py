async def test_get_page_source(context):
    async with context.driver.run(context.engine) as driver:
        async with driver.session(context.browser, context.base_url) as session:
            await session.get('/')
            assert 'Hello World!' in await session.get_page_source()


async def test_simple_form_submit(context):
    async with context.driver.run(context.engine) as driver:
        async with driver.session(context.browser, context.base_url) as session:
            await session.get('/html/')
            field = await session.get_element('input[name="field"]')
            await field.send_keys('sample input')
            submit = await session.get_element('input[type="submit"]')
            await submit.click()
            h2 = await driver.wait(5, session.get_element, 'h2')
            assert 'sample input' == await h2.get_text()


async def test_double_session(context):
    async with context.driver.run(context.engine) as driver:
        async with driver.session(context.browser, context.base_url) as session1, driver.session(context.browser, context.base_url) as session2:
            await session1.get('/name/foo/')
            await session2.get('/name/bar/')
            element1 = await driver.wait(5, session1.get_element, 'div')
            element2 = await driver.wait(5, session2.get_element, 'div')
            assert 'foo' == await element1.get_text()
            assert 'bar' == await element2.get_text()
