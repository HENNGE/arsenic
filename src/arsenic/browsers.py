from arsenic.session import Session, CompatSession


class Browser:
    defaults = {}
    session_class = Session

    def __init__(self, **overrides):
        self.capabilities = {**self.defaults, **overrides}


class Firefox(Browser):
    defaults = {
        'browserName': 'firefox',
        'marionette': True,
        'acceptInsecureCerts': True,
    }


class PhantomJS(Browser):
    session_class = CompatSession
    defaults = {
        'browserName': 'phantomjs',
        'version': '',
        'platform': 'ANY',
        'javascriptEnabled': True,
    }


class InternetExplorer(Browser):
    session_class = CompatSession
    defaults = {
        'browserName': 'internet explorer',
        'version': '',
        'platform': 'WINDOWS',
    }
