class ArsenicError(Exception):
    pass


CODES = {}


def get(error_code):
    return CODES.get(error_code, ArsenicError)


def create(error_code):
    name = ''.join(bit.capitalize() for bit in error_code.split(' '))
    cls = type(name, (ArsenicError,), {})
    CODES[error_code] = cls
    return cls


NoSuchElement = create('no such element')
