import attr


@attr.s
class Element:
    connection = attr.ib()

    async def get_text(self):
        return await self.connection.request(
            url='/text',
            method='GET'
        )

    async def send_keys(self, keys):
        await self.connection.request(
            url='/value',
            method='POST',
            data={
                'value': list(keys),
                'text': keys,
            }
        )

    async def click(self):
        await self.connection.request(
            url='/click',
            method='POST'
        )


@attr.s
class Session:
    connection = attr.ib()

    async def get(self, url: str):
        await self.connection.request(
            url='/url',
            method='POST',
            data={
                'url': url
            }
        )

    async def get_url(self):
        return await self.connection.request(
            url='/url',
            method='GET'
        )

    async def get_page_source(self):
        return await self.connection.request(
            url='/source',
            method='GET'
        )

    async def get_element(self, selector: str) -> Element:
        element_id = await self.connection.request(
            url='/element',
            method='POST',
            data={
                'using': 'css selector',
                'value': selector
            }
        )
        return Element(self.connection.prefixed(f'/element/{element_id}'))

    async def close(self):
        await self.connection.request(
            url='',
            method='DELETE'
        )


@attr.s
class SessionContext:
    driver = attr.ib()
    browser = attr.ib()
    session = attr.ib(default=None)

    async def __aenter__(self):
        self.session = await self.driver.new_session(self.browser)
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        self.session = None


@attr.s
class WebDriver:
    engine = attr.ib()
    connection = attr.ib()
    closers = attr.ib()

    def session(self, browser):
        return SessionContext(self, browser)

    async def new_session(self, browser) -> Session:
        response = await self.connection.request(
            url='/session',
            method='POST',
            data={
                'desiredCapabilities': browser.capabilities
            },
            raw=True,
        )
        if 'sessionId' not in response:
            response = response['value']
        session_id = response['sessionId']
        return Session(self.connection.prefixed(f'/session/{session_id}'))

    async def close(self):
        for closer in reversed(self.closers):
            await closer()
