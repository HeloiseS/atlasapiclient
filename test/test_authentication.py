import getpass
import io

import pytest
import requests

from atlasapiclient.authentication import Token
from atlasapiclient.exceptions import ATLASAPIClientAuthError
from .conftest import MockResponse

@pytest.fixture()
def dummy_token_str():
    return '1234567890123456789012345678901234567890'

@pytest.fixture()
def alt_dummy_token_str():
    return '1111111111111111111111111111111111111111'

@pytest.fixture()
def token(dummy_token_str):
    return Token(dummy_token_str)

class MockAuthResponse:
    def __init__(self, status_code, token_str):
        self.status_code = status_code
        self.json = lambda: {'token': token_str}
    
    def json(self):
        return self.json

class TestToken():
    def test_constructor(self, dummy_token_str):
        # 40 characters long str should work 
        token = Token(dummy_token_str)
        
    @pytest.mark.parametrize("token_str, expected_exception", [
        ("", ATLASAPIClientAuthError),
        ("123", ATLASAPIClientAuthError),
        ("12345678901234567890123456789012345678901", ATLASAPIClientAuthError),
        (None, ATLASAPIClientAuthError),
        (1, ATLASAPIClientAuthError),
        (True, ATLASAPIClientAuthError),
        (False, ATLASAPIClientAuthError),
        ({"key": "value"}, ATLASAPIClientAuthError),
        ([1, 2, 3], ATLASAPIClientAuthError),
    ])
    def test_constructor_bad(self, token_str, expected_exception):
        with pytest.raises(expected_exception):
            Token(token_str)
            
    def test_as_auth_header(self, token, dummy_token_str):
        assert token.as_auth_header() == f"Token {dummy_token_str}"
        
    def test_as_bearer_header(self, token, dummy_token_str):
        assert token.as_bearer_header() == f"Bearer {dummy_token_str}"
        
    def test_as_query_param(self, token, dummy_token_str):
        assert token.as_query_param() == dummy_token_str
        
    def test_as_cookie(self, token, dummy_token_str):
        cookie = token.as_cookie()
        assert isinstance(cookie, dict)
        assert "token" in cookie
        assert token.as_cookie() == {"token": dummy_token_str}
        
    def test_validate(self, token, alt_dummy_token_str):
        token.val = alt_dummy_token_str
        token.validate()
        assert token.val == alt_dummy_token_str
        
    @pytest.mark.parametrize("token_str", [
        "12345678901234567890123456789012345678901",
        "123456789012345678901234567890123456789",
        "123",
        "",
        0,
        True,
        False,
        None,
        {"key": "value"},
        [1, 2, 3],
    ])
    def test_validate_bad(self, token, token_str):
        token.val = token_str
        with pytest.raises(ATLASAPIClientAuthError):
            token.validate()
    
    def test_refresh_200(self, monkeypatch, token, alt_dummy_token_str):
        monkeypatch.setattr(requests, 'post', 
                            lambda *args, **kwargs: MockAuthResponse(200, alt_dummy_token_str))
        monkeypatch.setattr(Token, 'get_username_password', lambda _: ('username', 'password'))
        token.refresh('http://localhost:8000/')
        assert token.val == alt_dummy_token_str
    
    @pytest.mark.parametrize("status_code", [400, 401, 403, 404, 500])
    def test_refresh_error_codes(self, monkeypatch, token, dummy_token_str, status_code):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse(status_code))
        monkeypatch.setattr(Token, 'get_username_password', lambda _: ('username', 'password'))
        with pytest.raises(ATLASAPIClientAuthError):
            token.refresh('http://localhost:8000/')
        assert token.val == dummy_token_str
            
    def test_refresh_error_invalid_token(self, monkeypatch, token):
        invalid_token_str = 'invalid_token'
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockAuthResponse(200, invalid_token_str))
        monkeypatch.setattr(Token, 'get_username_password', lambda _: ('username', 'password'))
        with pytest.raises(ATLASAPIClientAuthError):
            token.refresh('http://localhost:8000/')
            
    @pytest.mark.parametrize("url", [None, 0, 1, True, False, {"key": "value"}, [1, 2, 3]])
    def test_refresh_error_base_url(self, monkeypatch, token, url):
        monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockAuthResponse(200, token.val))
        monkeypatch.setattr(Token, 'get_username_password', lambda _: ('username', 'password'))
        with pytest.raises(ATLASAPIClientAuthError):
            token.refresh(url)
            
    def test_get_username_password(self, monkeypatch):
        monkeypatch.setattr('sys.stdin', io.StringIO('username'))
        monkeypatch.setattr(getpass, 'getpass', lambda _: 'password')
        username, password = Token.get_username_password()
        assert username == 'username'
        assert password == 'password'