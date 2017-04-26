class Browser:
    defaults = {}

    def __init__(self, overrides=None):
        self.capabilities = {**self.defaults}
        if overrides is not None:
            self.capabilities.update(overrides)


class Firefox(Browser):
    defaults = {
        'browserName': 'firefox',
        'marionette': True,
        'acceptInsecureCerts': True,
    }
