import pytest

from arsenic.connection import strip_auth
from arsenic.http import BasicAuth
from arsenic.services import auth_or_string


@pytest.mark.parametrize('url,result', [
    ('http://foo:bar@baz.com', 'http://baz.com'),
    ('http://bar.com', 'http://bar.com'),
    ('http://foo@bar.com', 'http://bar.com'),
])
def test_strip_auth(url, result):
    assert strip_auth(url) == result


def test_auth_string():
    assert auth_or_string('hello:world') == BasicAuth('hello', 'world')
    assert auth_or_string(None) == None
    assert auth_or_string(BasicAuth('foo', 'bar')) == BasicAuth('foo', 'bar')
    with pytest.raises(TypeError):
        auth_or_string(1)
