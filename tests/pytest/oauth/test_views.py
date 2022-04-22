from django.http import HttpResponse
from django.urls import reverse

from benefits.core import session
from benefits.oauth.views import (
    ROUTE_START,
    ROUTE_CONFIRM,
    login,
    authorize,
    logout,
    post_logout,
    _deauthorize_redirect,
    _generate_redirect_uri,
)
import benefits.oauth.views

import pytest


@pytest.mark.request_path("/oauth/login")
def test_login(mocker, session_request):
    mock_client = mocker.patch.object(benefits.oauth.views, "oauth_client")
    mock_client.authorize_redirect.return_value = HttpResponse("authorize redirect")

    assert session.oauth_token(session_request) is None

    login(session_request)

    mock_client.authorize_redirect.assert_called_with(session_request, "https://testserver/oauth/authorize")
    assert session.oauth_token(session_request) is None


@pytest.mark.request_path("/oauth/login")
def test_authorize_fail(mocker, session_request):
    mock_client = mocker.patch.object(benefits.oauth.views, "oauth_client")
    mock_client.authorize_access_token.return_value = None

    assert session.oauth_token(session_request) is None

    result = authorize(session_request)

    mock_client.authorize_access_token.assert_called_with(session_request)
    assert session.oauth_token(session_request) is None
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_START)


@pytest.mark.request_path("/oauth/login")
def test_authorize_success(mocker, session_request):
    mock_client = mocker.patch.object(benefits.oauth.views, "oauth_client")
    mock_client.authorize_access_token.return_value = {"id_token": "token"}

    result = authorize(session_request)

    mock_client.authorize_access_token.assert_called_with(session_request)
    assert session.oauth_token(session_request) == "token"
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


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
    assert not session.logged_in(session_request)
    assert session.enrollment_token(session_request) is False


@pytest.mark.request_path("/oauth/post_logout")
def test_post_logout(session_request):
    origin = reverse("core:index")
    session.update(session_request, origin=origin)

    result = post_logout(session_request)

    assert result.status_code == 302
    assert result.url == origin


def test_deauthorize_redirect(mocker):
    mock_client = mocker.patch.object(benefits.oauth.views, "oauth_client")
    mock_client.load_server_metadata.return_value = {"end_session_endpoint": "https://server/endsession"}

    result = _deauthorize_redirect("token", "https://localhost/redirect_uri")

    mock_client.load_server_metadata.assert_called()
    assert result.status_code == 302
    assert (
        result.url
        == "https://server/endsession?id_token_hint=token&post_logout_redirect_uri=https%3A%2F%2Flocalhost%2Fredirect_uri"
    )


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
