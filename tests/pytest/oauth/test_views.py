from django.http import HttpResponse
from django.urls import reverse

from authlib.integrations.django_client.apps import DjangoOAuth2App
import pytest

from benefits.core import session
from benefits.core.views import ROUTE_INDEX

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


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.views)


@pytest.fixture
def mocked_oauth_client(mocker):
    mock_client = mocker.Mock(spec=DjangoOAuth2App)
    mocker.patch("benefits.oauth.views.client.instance", return_value=mock_client)
    return mock_client


@pytest.mark.usefixtures("mocked_analytics_module")
def test_login(mocked_oauth_client, app_request):
    assert not session.logged_in(app_request)

    mocked_oauth_client.authorize_redirect.return_value = HttpResponse("authorize redirect")

    login(app_request)

    mocked_oauth_client.authorize_redirect.assert_called_with(app_request, "https://testserver/oauth/authorize")
    assert not session.logged_in(app_request)


@pytest.mark.usefixtures("mocked_oauth_client")
def test_login_analytics(mocked_analytics_module, app_request):
    login(app_request)

    mocked_analytics_module.started_sign_in.assert_called_once()


def test_authorize_fail(mocked_oauth_client, app_request):
    mocked_oauth_client.authorize_access_token.return_value = None

    assert not session.logged_in(app_request)

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert not session.logged_in(app_request)
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_START)


@pytest.mark.usefixtures("mocked_analytics_module")
def test_authorize_success(mocked_oauth_client, app_request):
    mocked_oauth_client.authorize_access_token.return_value = {"id_token": "token"}

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert session.logged_in(app_request)
    assert session.oauth_token(app_request) == "token"
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


def test_authorize_analytics(mocked_analytics_module, mocked_oauth_client, app_request):
    mocked_oauth_client.authorize_access_token.return_value = {"id_token": "token"}

    authorize(app_request)

    mocked_analytics_module.finished_sign_in.assert_called_once()


@pytest.mark.usefixtures("mocked_analytics_module")
def test_logout(mocker, app_request):
    # logout internally calls _deauthorize_redirect
    # this mocks that function and a success response
    # and returns a spy object we can use to validate calls
    message = "logout successful"
    spy = mocker.patch("benefits.oauth.views._deauthorize_redirect", return_value=HttpResponse(message))

    token = "token"
    session.update(app_request, oauth_token=token)
    assert session.oauth_token(app_request) == token

    result = logout(app_request)

    spy.assert_called_with(token, "https://testserver/oauth/post_logout")
    assert result.status_code == 200
    assert message in str(result.content)
    assert not session.logged_in(app_request)
    assert session.enrollment_token(app_request) is False


def test_logout_analytics(mocker, mocked_analytics_module, app_request):
    # logout internally calls _deauthorize_redirect
    # this mocks that function and a success response
    message = "logout successful"
    mocker.patch("benefits.oauth.views._deauthorize_redirect", return_value=HttpResponse(message))

    token = "token"
    session.update(app_request, oauth_token=token)
    assert session.oauth_token(app_request) == token

    logout(app_request)

    mocked_analytics_module.started_sign_out.assert_called_once()


@pytest.mark.usefixtures("mocked_analytics_module")
def test_post_logout(app_request):
    origin = reverse(ROUTE_INDEX)
    session.update(app_request, origin=origin)

    result = post_logout(app_request)

    assert result.status_code == 302
    assert result.url == origin


def test_post_logout_analytics(mocked_analytics_module, app_request):
    post_logout(app_request)

    mocked_analytics_module.finished_sign_out.assert_called_once()


def test_deauthorize_redirect(mocked_oauth_client):
    mocked_oauth_client.load_server_metadata.return_value = {"end_session_endpoint": "https://server/endsession"}

    result = _deauthorize_redirect("token", "https://localhost/redirect_uri")

    mocked_oauth_client.load_server_metadata.assert_called()
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
