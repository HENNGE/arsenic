import pytest

from arsenic.connection import strip_auth


@pytest.mark.parametrize('url,result', [
    ('http://foo:bar@baz.com', 'http://baz.com'),
    ('http://bar.com', 'http://bar.com'),
    ('http://foo@bar.com', 'http://bar.com'),
])
def test_strip_auth(url, result):
    assert strip_auth(url) == result
