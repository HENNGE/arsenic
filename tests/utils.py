import os


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fobj:
        return fobj.read()
