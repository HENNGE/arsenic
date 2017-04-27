import os


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), 'templates', fname)) as fobj:
        return fobj.read()


def ids_from_params(params):
    for ec, sc in params:
        yield f'{ec.name}-{sc.name}'
