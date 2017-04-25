import os

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common import utils

from arsenic.clients import Client, Request


class Service:
    def __init__(self, client: Client, executable, port=0, log_file=os.devnull,
                 env=None, start_error_message=""):
        self.client = client
        self.path = executable
        self.port = port
        if self.port == 0:
            self.port = utils.free_port()
        self.start_error_message = start_error_message
        self.log_file = log_file
        self.env = env or os.environ
        self.process = None

    @property
    def service_url(self):
        """
        Gets the url of the Service
        """
        return f"http://{utils.join_host_port('localhost', self.port)}"

    def command_line_args(self):
        raise NotImplemented("This method needs to be implemented in a sub class")

    async def start(self):
        """
        Starts the Service.

        :Exceptions:
         - WebDriverException : Raised either when it can't start the service
           or when it can't connect to the service
        """
        try:
            cmd = [self.path]
            cmd.extend(self.command_line_args())
            self.process = await self.client.start_process(
                cmd=cmd,
                env=self.env,
                log=self.log_file,
            )
        except Exception as e:
            raise WebDriverException(
                "The executable %s needs to be available in the path. %s\n%s" %
                (os.path.basename(self.path), self.start_error_message, str(e)))
        count = 0
        while True:
            await self.assert_process_still_running()
            if await self.is_connectable():
                break
            count += 1
            await self.client.sleep(1)
            if count == 30:
                raise WebDriverException("Can not connect to the Service %s" % self.path)

    async def assert_process_still_running(self):
        if not await self.client.process_running(self.process):
            return_code = await self.client.process_return_code(self.process)
            raise WebDriverException(
                'Service %s unexpectedly exited. Status code was: %s'
                % (self.path, return_code)
            )

    async def is_connectable(self):
        return utils.is_connectable(self.port)

    async def send_remote_shutdown_command(self):
        session = await self.client.init_session()
        try:
            await self.client.send_request(session, Request(
                url=f'{self.service_url}/shutdown',
                method='GET',
            ))
        finally:
            await self.client.close_session(session)

        for x in range(30):
            if not await self.is_connectable():
                break
            else:
                await self.client.sleep(1)

    async def stop(self):
        """
        Stops the service.
        """
        if not self.log_file == os.devnull:
            try:
                self.log_file.close()
            except Exception:
                pass

        if self.process is None:
            return

        try:
            await self.send_remote_shutdown_command()
        except TypeError:
            pass

        try:
            if self.process:
                for stream in [self.process.stdin,
                               self.process.stdout,
                               self.process.stderr]:
                    try:
                        stream.close()
                    except AttributeError:
                        pass
                await self.client.terminate_process(self.process)
                self.process = None
        except OSError:
            pass
