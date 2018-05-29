import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import os

import arsenic
from .utils import find_binary

DOCS_DIR = os.environ.get(
    "DOCS_DIR", Path(arsenic.__file__).parent.parent.parent / "docs"
)


def test_docs_build():
    binary = find_binary("sphinx-build")
    with TemporaryDirectory() as workspace:
        subprocess.check_call([binary, "-M", "html", str(DOCS_DIR), workspace])
