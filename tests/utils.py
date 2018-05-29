import os
from contextlib import contextmanager
from shutil import which

import pytest as pytest


@contextmanager
def null_context():
    yield


def find_binary(name: str) -> str:
    candidates = [
        os.environ.get(f'{name.upper().replace("-", "_")}_BINARY', ""),
        name,
        f"{name}.exe",
    ]
    for candidate in candidates:
        path = which(candidate)
        if path:
            return path
    raise pytest.skip(f"Could not find driver {name!r}, skipping")
