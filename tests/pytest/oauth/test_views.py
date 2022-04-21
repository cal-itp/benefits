from django.http import HttpResponse

from benefits.core import session
from benefits.oauth.views import logout, _generate_redirect_uri

import pytest


@pytest.mark.request_path("/oauth/logout")
def test_logout(mocker, session_request):
    # logout internally calls _deauthorize_redirect
    # this mocks that function and a success response
    # and returns a spy object we can use to validate calls
    spy = mocker.patch("benefits.oauth.views._deauthorize_redirect", return_value=HttpResponse("logout successful"))

    session.update(session_request, oauth_token="token")
    assert session.oauth_token(session_request) == "token"

    result = logout(session_request)

    spy.assert_called_with("token", "https://testserver/oauth/post_logout")
    assert result.status_code == 200
    assert "logout successful" in str(result.content)
    assert session.oauth_token(session_request) is False


def test_generate_redirect_uri_default(rf):
    request = rf.get("/oauth/login")
    path = "/test"

    redirect_uri = _generate_redirect_uri(request, path)

    assert redirect_uri == "https://testserver/test"


def test_generate_redirect_uri_localhost(rf):
    request = rf.get("/oauth/login", SERVER_NAME="localhost")
    path = "/test"

    redirect_uri = _generate_redirect_uri(request, path)

    assert redirect_uri == "http://localhost/test"
