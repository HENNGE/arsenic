import pytest
import sys

from arsenic.services import Geckodriver

pytestmark = [pytest.mark.asyncio]


@pytest.mark.parametrize(
    "version,check,result",
    [("0.17", True, True), ("0.16", True, False), ("0.16", False, True)],
)
@pytest.mark.skipif(sys.platform == "win32", reason="Not supported on windows")
async def test_geckodriver_version_ok(tmpdir, version, check, result):
    path = tmpdir.join("geckodriver")
    path.write(f'#!{sys.executable}\nprint("geckodriver {version}")')
    path.chmod(0o755)
    driver = Geckodriver(binary=str(path), version_check=check)
    if result:
        await driver._check_version()
    else:
        with pytest.raises(ValueError):
            await driver._check_version()
