import pytest

from arsenic.services import Geckodriver

pytestmark = pytest.mark.asyncio


async def test_geckodriver_version_ok(tmpdir):
    path = tmpdir.join(
        'geckodriver'
    )
    path.write('#!/usr/bin/env python3\nprint("geckodriver 0.17")')
    path.chmod(0o755)
    driver = Geckodriver(binary=str(path))
    await driver._check_version()


async def test_geckodriver_version_bad(tmpdir):
    path = tmpdir.join(
        'geckodriver'
    )
    path.write('#!/usr/bin/env python3\nprint("geckodriver 0.16")')
    path.chmod(0o755)
    driver = Geckodriver(binary=str(path))
    with pytest.raises(ValueError):
        await driver._check_version()


async def test_geckodriver_version_ignore(tmpdir):
    path = tmpdir.join(
        'geckodriver'
    )
    path.write('#!/usr/bin/env python3\nprint("geckodriver 0.16")')
    path.chmod(0o755)
    driver = Geckodriver(binary=str(path), version_check=False)
    await driver._check_version()
