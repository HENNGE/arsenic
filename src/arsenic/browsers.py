from typing import Any, Dict

from arsenic.session import Session


class Browser:
    defaults = {}
    session_class = Session

    def __init__(self, **overrides):
        self.capabilities = {**self.defaults, **overrides}

    def build_capabilities(self) -> Dict[str, Any]:
        return {"capabilities": {"alwaysMatch": self.capabilities}}


class Firefox(Browser):
    defaults = {"browserName": "firefox", "acceptInsecureCerts": True}


class Chrome(Browser):
    defaults = {"browserName": "chrome"}


class InternetExplorer(Browser):
    session_class = Session
    defaults = {
        "browserName": "internet explorer",
        "version": "",
        "platform": "WINDOWS",
    }

    def build_capabilities(self) -> Dict[str, Any]:
        return {"desiredCapabilities": self.capabilities}


IE = InternetExplorer
