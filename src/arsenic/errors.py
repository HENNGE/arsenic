class ArsenicError(Exception):
    pass


class UnknownArsenicError(ArsenicError):
    def __init__(self, message, screen, stacktrace):
        self.message = message
        self.screen = screen
        self.stacktrace = stacktrace
        super().__init__(message)


CODES = {}


def get(error_code):
    return CODES.get(error_code, UnknownArsenicError)


def create(error_name, *error_codes):
    name = ''.join(bit.capitalize() for bit in error_name.split(' '))
    cls = type(name, (ArsenicError,), {})
    CODES[error_name] = cls
    for code in error_codes:
        CODES[error_name] = cls
    return cls


NoSuchElement = create('no such element', 7)
NoSuchFrame = create('no such frame', 8)
UnknownCommand = create('unknown command', 9)
StaleElementReference = create('stale element reference', 10)
ElementNotVisible = create('element not visible', 11)
InvalidElementState = create('invalid element state', 12)
UnknownError = create('unknown error', 13)
ElementNotInteractable = create('element not interactable')
ElementIsNotSelectable = create('element is not selectable', 15)
JavascriptError = create('javascript error', 17)
Timeout = create('timeout', 21)
NoSuchWindow = create('no such window', 23)
InvalidCookieDomain = create('invalid cookie domain', 24)
UnableToSetCookie = create('unable to set cookie', 25)
UnexpectedAlertOpen = create('unexpected alert open', 26)
NoSuchAlert = create('no such alert', 27)
ScriptTimeout = create('script timeout', 28)
InvalidElementCoordinates = create('invalid element coordinates', 29)
IMENotAvailable = create('ime not available', 30)
IMEEngineActivationFailed = create('ime engine activation failed', 31)
InvalidSelector = create('invalid selector', 32)
MoveTargetOutOfBounds = create('move target out of bounds', 34)


def _value_or_default(obj, key, default):
    return obj[key] if key in obj else default


def check_response(data):
    status = data.get('status', None)
    if status is None or status == 0:
        return

    value = None
    message = data.get("message", "")
    screen = data.get("screen", "")
    stacktrace = None
    if isinstance(status, int):
        value_json = data.get('value', None)
        if value_json and isinstance(value_json, str):
            import json
            try:
                value = json.loads(value_json)
                if len(value.keys()) == 1:
                    value = value['value']
                status = value.get('error', None)
                if status is None:
                    status = value["status"]
                    message = value["value"]
                    if not isinstance(message, str):
                        value = message
                        message = message.get('message')
                else:
                    message = value.get('message', None)
            except ValueError:
                pass

    exception_class = get(status)
    if value == '' or value is None:
        value = data['value']
    if isinstance(value, str):
        if exception_class is ArsenicError:
            raise exception_class(data, value)
        raise exception_class(value)
    if message == "" and 'message' in value:
        message = value['message']

    screen = None
    if 'screen' in value:
        screen = value['screen']

    stacktrace = None
    if 'stackTrace' in value and value['stackTrace']:
        stacktrace = []
        try:
            for frame in value['stackTrace']:
                line = frame.get('lineNumber', '')
                file = frame.get('fileName', '<anonymous>')
                if line:
                    file = f"{file}:{line}"
                meth = frame.get('methodName', '<anonymous>')
                if 'className' in frame:
                    meth = f"{frame['className']}.{meth}"
                msg = f"    at {meth} ({file})"
                stacktrace.append(msg)
        except TypeError:
            pass
    raise exception_class(message, screen, stacktrace)
