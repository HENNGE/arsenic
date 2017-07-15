import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

DOCS_DIR = os.environ.get('DOCS_DIR', str(Path(__file__).parent.parent.parent / 'docs'))
SPHINXBUILD = os.environ.get('SPHINXBUILD', 'sphinx-build')

def test_docs_build():
    with TemporaryDirectory() as workspace:
        subprocess.check_call([SPHINXBUILD, '-M', 'html', DOCS_DIR, workspace])
