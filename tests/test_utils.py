import pytest

from arsenic.connection import strip_auth
from arsenic.http import BasicAuth
from arsenic.services import auth_or_string
from arsenic.utils import px_to_number


@pytest.mark.parametrize(
    "url,result",
    [
        ("http://foo:bar@baz.com", "http://baz.com"),
        ("http://bar.com", "http://bar.com"),
        ("http://foo@bar.com", "http://bar.com"),
    ],
)
def test_strip_auth(url, result):
    assert strip_auth(url) == result


def test_auth_string():
    assert auth_or_string("hello:world") == BasicAuth("hello", "world")
    assert auth_or_string(None) == None
    assert auth_or_string(BasicAuth("foo", "bar")) == BasicAuth("foo", "bar")
    with pytest.raises(TypeError):
        auth_or_string(1)


@pytest.mark.parametrize(
    "px,number", [("1", 1), ("1.2", 1.2), ("2px", 2), ("3.4px", 3.4)]
)
def test_px_to_number(px, number):
    assert px_to_number(px) == number
