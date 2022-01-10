from arsenic.session import Session


class Browser:
    defaults = {}
    session_class = Session

    def __init__(self, **overrides):
        self.capabilities = {**self.defaults, **overrides}


class Firefox(Browser):
    defaults = {"browserName": "firefox"}


class Chrome(Browser):
    defaults = {"browserName": "chrome"}


class InternetExplorer(Browser):
    session_class = Session
    defaults = {"browserName": "internet explorer"}


IE = InternetExplorer


class MicrosoftEdge(Browser):
    defaults = {"browserName": "MicrosoftEdge"}


Edge = MicrosoftEdge
