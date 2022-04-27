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


def test_login(mocker, app_request):
    mock_client = mocker.patch.object(benefits.oauth.views, "oauth_client")
    mock_client.authorize_redirect.return_value = HttpResponse("authorize redirect")

    mocker.patch.object(benefits.oauth.views, "analytics")

    assert not session.logged_in(app_request)

    login(app_request)

    mock_client.authorize_redirect.assert_called_with(app_request, "https://testserver/oauth/authorize")
    assert not session.logged_in(app_request)


def test_login_analytics(mocker, app_request):
    spy = mocker.patch("benefits.oauth.analytics.started_sign_in")

    mock_client = mocker.patch.object(benefits.oauth.views, "oauth_client")
    mock_client.authorize_redirect.return_value = HttpResponse("authorize redirect")

    login(app_request)

    spy.assert_called_once()


def test_authorize_fail(mocker, app_request):
    mock_client = mocker.patch.object(benefits.oauth.views, "oauth_client")
    mock_client.authorize_access_token.return_value = None

    assert not session.logged_in(app_request)

    result = authorize(app_request)

    mock_client.authorize_access_token.assert_called_with(app_request)
    assert not session.logged_in(app_request)
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_START)


def test_authorize_success(mocker, app_request):
    mock_client = mocker.patch.object(benefits.oauth.views, "oauth_client")
    mock_client.authorize_access_token.return_value = {"id_token": "token"}

    mocker.patch.object(benefits.oauth.views, "analytics")

    result = authorize(app_request)

    mock_client.authorize_access_token.assert_called_with(app_request)
    assert session.logged_in(app_request)
    assert session.oauth_token(app_request) == "token"
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


def test_authorize_analytics(mocker, app_request):
    spy = mocker.patch("benefits.oauth.analytics.finished_sign_in")

    mock_client = mocker.patch.object(benefits.oauth.views, "oauth_client")
    mock_client.authorize_access_token.return_value = {"id_token": "token"}

    authorize(app_request)

    spy.assert_called_once()


def test_logout(mocker, app_request):
    # logout internally calls _deauthorize_redirect
    # this mocks that function and a success response
    # and returns a spy object we can use to validate calls
    message = "logout successful"
    spy = mocker.patch("benefits.oauth.views._deauthorize_redirect", return_value=HttpResponse(message))

    mocker.patch.object(benefits.oauth.views, "analytics")

    token = "token"
    session.update(app_request, oauth_token=token)
    assert session.oauth_token(app_request) == token

    result = logout(app_request)

    spy.assert_called_with(token, "https://testserver/oauth/post_logout")
    assert result.status_code == 200
    assert message in str(result.content)
    assert not session.logged_in(app_request)
    assert session.enrollment_token(app_request) is False


def test_logout_analytics(mocker, app_request):
    spy = mocker.patch("benefits.oauth.analytics.started_sign_out")

    # logout internally calls _deauthorize_redirect
    # this mocks that function and a success response
    message = "logout successful"
    mocker.patch("benefits.oauth.views._deauthorize_redirect", return_value=HttpResponse(message))

    token = "token"
    session.update(app_request, oauth_token=token)
    assert session.oauth_token(app_request) == token

    logout(app_request)

    spy.assert_called_once()


def test_post_logout(mocker, app_request):
    origin = reverse("core:index")
    session.update(app_request, origin=origin)

    mocker.patch.object(benefits.oauth.views, "analytics")

    result = post_logout(app_request)

    assert result.status_code == 302
    assert result.url == origin


def test_post_logout_analytics(mocker, app_request):
    spy = mocker.patch("benefits.oauth.analytics.finished_sign_out")

    post_logout(app_request)

    spy.assert_called_once()


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
