from selenium.webdriver.chrome.options import Options

from arsenic.connection import RemoteConnection
from arsenic.service import Service
from .remote import RemoteDriver


class ChromeRemoteConnection(RemoteConnection):
    def __init__(self, client, *, remote_server_addr):
        super().__init__(client, remote_server_addr=remote_server_addr)
        self._commands["launchApp"] = ('POST', '/session/$sessionId/chromium/launch_app')


class ChromeService(Service):
    """
    Object that manages the starting and stopping of the ChromeDriver
    """

    def __init__(self, client, executable_path, port=0, service_args=None,
                 log_path=None, env=None):
        """
        Creates a new instance of the Service

        :Args:
         - executable_path : Path to the ChromeDriver
         - port : Port the service is running on
         - service_args : List of args to pass to the chromedriver service
         - log_path : Path for the chromedriver service to log to"""

        self.service_args = service_args or []
        if log_path:
            self.service_args.append('--log-path=%s' % log_path)

        super().__init__(
            client,
            executable_path,
            port=port,
            env=env,
            start_error_message="Please see https://sites.google.com/a/chromium.org/chromedriver/home"
        )

    def command_line_args(self):
        return [f"--port={self.port:d}"] + self.service_args


class ChromeDriver(RemoteDriver):
    """
    Controls the ChromeDriver and allows you to drive the browser.

    You will need to download the ChromeDriver executable from
    http://chromedriver.storage.googleapis.com/index.html
    """

    def __init__(self, client, executable_path="chromedriver", port=0,
                 chrome_options=None, service_args=None,
                 desired_capabilities=None, service_log_path=None):
        """
        Creates a new instance of the chrome driver.

        Starts the service and then creates new instance of chrome driver.

        :Args:
         - executable_path - path to the executable. If the default is used it assumes the executable is in the $PATH
         - port - port you would like the service to run, if left as 0, a free port will be found.
         - desired_capabilities: Dictionary object with non-browser specific
           capabilities only, such as "proxy" or "loggingPref".
         - chrome_options: this takes an instance of ChromeOptions
        """
        if chrome_options is None:
            # desired_capabilities stays as passed in
            if desired_capabilities is None:
                desired_capabilities = self.create_options().to_capabilities()
        else:
            if desired_capabilities is None:
                desired_capabilities = chrome_options.to_capabilities()
            else:
                desired_capabilities.update(chrome_options.to_capabilities())

        self.service = ChromeService(
            client,
            executable_path,
            port=port,
            service_args=service_args,
            log_path=service_log_path
        )

        try:
            super().__init__(
                client,
                command_executor=ChromeRemoteConnection(
                    client,
                    remote_server_addr=self.service.service_url
                ),
                desired_capabilities=desired_capabilities
            )
        except Exception:
            self.quit()
            raise
        self._is_remote = False

    async def async_setup(self):
        await self.service.start()
        await super().async_setup()

    async def quit(self):
        """
        Closes the browser and shuts down the ChromeDriver executable
        that is started when starting the ChromeDriver
        """
        try:
            await super().quit()
        except Exception:
            # We don't care about the message because something probably has gone wrong
            pass
        finally:
            await self.service.stop()

    def create_options(self):
        return Options()
