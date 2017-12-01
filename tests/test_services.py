import pytest
import sys

from arsenic.services import Geckodriver

pytestmark = [
    pytest.mark.asyncio
]

@pytest.mark.skipif(sys.platform == 'win32', reason='Not supported on windows')
async def test_geckodriver_version_ok(tmpdir):
    path = tmpdir.join(
        'geckodriver'
    )
    path.write('#!/usr/bin/env python3.6\nprint("geckodriver 0.17")')
    path.chmod(0o755)
    driver = Geckodriver(binary=str(path))
    await driver._check_version()


@pytest.mark.skipif(sys.platform == 'win32', reason='Not supported on windows')
async def test_geckodriver_version_bad(tmpdir):
    path = tmpdir.join(
        'geckodriver'
    )
    path.write('#!/usr/bin/env python3.6\nprint("geckodriver 0.16")')
    path.chmod(0o755)
    driver = Geckodriver(binary=str(path))
    with pytest.raises(ValueError):
        await driver._check_version()


@pytest.mark.skipif(sys.platform == 'win32', reason='Not supported on windows')
async def test_geckodriver_version_ignore(tmpdir):
    path = tmpdir.join(
        'geckodriver'
    )
    path.write('#!/usr/bin/env python3.6\nprint("geckodriver 0.16")')
    path.chmod(0o755)
    driver = Geckodriver(binary=str(path), version_check=False)
    await driver._check_version()
