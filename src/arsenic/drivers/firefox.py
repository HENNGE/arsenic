from selenium.webdriver import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webelement import FirefoxWebElement

from arsenic.connection import RemoteConnection
from arsenic.drivers import RemoteDriver
from arsenic.service import Service

import shutil
import sys

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class FirefoxService(Service):
    def __init__(self, client, executable_path, port=0, service_args=None,
                 log_path=None, env=None):
        log_file = open(log_path, "a+") if log_path is not None and log_path != "" else None

        super().__init__(
            client,
            executable_path,
            port=port,
            log_file=log_file,
            env=env
        )
        self.service_args = service_args or []

    def command_line_args(self):
        return ["--port", "%d" % self.port]

    async def send_remote_shutdown_command(self):
        pass


class FirefoxRemoteConnection(RemoteConnection):
    def __init__(self, client, *, remote_server_addr):
        super().__init__(client, remote_server_addr=remote_server_addr)
        self._commands["GET_CONTEXT"] = ('GET', '/session/$sessionId/moz/context')
        self._commands["SET_CONTEXT"] = ("POST", "/session/$sessionId/moz/context")
        self._commands["ELEMENT_GET_ANONYMOUS_CHILDREN"] = \
            ("POST", "/session/$sessionId/moz/xbl/$id/anonymous_children")
        self._commands["ELEMENT_FIND_ANONYMOUS_ELEMENTS_BY_ATTRIBUTE"] = \
            ("POST", "/session/$sessionId/moz/xbl/$id/anonymous_by_attribute")


class FirefoxContext:
    def __init__(self, driver, context):
        self.driver = driver
        self.context = context

    async def __aenter__(self):
        initial_context = await self.execute('GET_CONTEXT').pop('value')
        await self.set_context(self.context)
        try:
            yield
        finally:
            await self.set_context(initial_context)



class FirefoxDriver(RemoteDriver):
    # There is no native event support on Mac
    NATIVE_EVENTS_ALLOWED = sys.platform != "darwin"

    CONTEXT_CHROME = "chrome"
    CONTEXT_CONTENT = "content"

    _web_element_cls = FirefoxWebElement

    def __init__(self, client, firefox_profile=None, firefox_binary=None,
                 timeout=30, capabilities=None, proxy=None,
                 executable_path="geckodriver", firefox_options=None,
                 log_path="geckodriver.log"):
        self.binary = None
        self.profile = None
        self.service = None

        if capabilities is None:
            capabilities = DesiredCapabilities.FIREFOX.copy()
        if firefox_options is None:
            firefox_options = Options()

        if capabilities.get("binary"):
            self.binary = capabilities["binary"]

        # firefox_options overrides capabilities
        if firefox_options is not None:
            if firefox_options.binary is not None:
                self.binary = firefox_options.binary
            if firefox_options.profile is not None:
                self.profile = firefox_options.profile

        # firefox_binary and firefox_profile
        # override firefox_options
        if firefox_binary is not None:
            if isinstance(firefox_binary, str):
                firefox_binary = FirefoxBinary(firefox_binary)
            self.binary = firefox_binary
            firefox_options.binary = firefox_binary
        if firefox_profile is not None:
            if isinstance(firefox_profile, str):
                firefox_profile = FirefoxProfile(firefox_profile)
            self.profile = firefox_profile
            firefox_options.profile = firefox_profile

        # W3C remote
        # TODO(ato): Perform conformance negotiation

        if capabilities.get("marionette"):
            capabilities.pop("marionette")
            self.service = FirefoxService(
                client,
                executable_path,
                log_path=log_path
            )

            capabilities.update(firefox_options.to_capabilities())

            executor = FirefoxRemoteConnection(
                client,
                remote_server_addr=self.service.service_url
            )
            super().__init__(
                client,
                command_executor=executor,
                desired_capabilities=capabilities,
            )

        # Selenium remote
        else:
            raise NotImplementedError()

        self._is_remote = False

    async def async_setup(self):
        await self.service.start()
        await super().async_setup()

    async def quit(self):
        """Quits the driver and close every associated window."""
        try:
            await super().quit()
        except:
            # Happens if Firefox shutsdown before we've read the response from
            # the socket.
            pass

        if self.w3c:
            await self.service.stop()
        else:
            self.binary.kill()

        if self.profile is not None:
            try:
                shutil.rmtree(self.profile.path)
                if self.profile.tempfolder is not None:
                    shutil.rmtree(self.profile.tempfolder)
            except Exception as e:
                print(str(e))

    @property
    def firefox_profile(self):
        return self.profile

    # Extension commands:

    async def set_context(self, context):
        await self.execute("SET_CONTEXT", {"context": context})

    def context(self, context):
        """Sets the context that Selenium commands are running in using
        a `with` statement. The state of the context on the server is
        saved before entering the block, and restored upon exiting it.

        :param context: Context, may be one of the class properties
            `CONTEXT_CHROME` or `CONTEXT_CONTENT`.

        Usage example::

            with selenium.context(selenium.CONTEXT_CHROME):
                # chrome scope
                ... do stuff ...
        """
        return FirefoxContext(self, context)
