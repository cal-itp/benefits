from django.http import HttpResponse
from django.urls import reverse

from benefits.core import session
from benefits.oauth.views import logout, post_logout, _generate_redirect_uri

import pytest


@pytest.mark.request_path("/oauth/logout")
def test_logout(mocker, session_request):
    # logout internally calls _deauthorize_redirect
    # this mocks that function and a success response
    # and returns a spy object we can use to validate calls
    message = "logout successful"
    spy = mocker.patch("benefits.oauth.views._deauthorize_redirect", return_value=HttpResponse(message))

    token = "token"
    session.update(session_request, oauth_token=token)
    assert session.oauth_token(session_request) == token

    result = logout(session_request)

    spy.assert_called_with(token, "https://testserver/oauth/post_logout")
    assert result.status_code == 200
    assert message in str(result.content)
    assert session.oauth_token(session_request) is False


@pytest.mark.request_path("/oauth/post_logout")
def test_post_logout(session_request):
    origin = reverse("core:index")
    session.update(session_request, origin=origin)

    result = post_logout(session_request)

    assert result.status_code == 302
    assert result.url == origin


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
