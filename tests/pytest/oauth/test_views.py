from django.http import HttpResponse
from django.urls import reverse

import pytest

from benefits.core import session
from benefits.core.views import ROUTE_INDEX

from benefits.oauth.views import ROUTE_START, ROUTE_CONFIRM, login, authorize, logout, post_logout
import benefits.oauth.views


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.views)


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
    spy = mocker.patch("benefits.oauth.views.redirects.deauthorize_redirect", return_value=HttpResponse(message))

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
    mocker.patch("benefits.oauth.views.redirects.deauthorize_redirect", return_value=HttpResponse(message))

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
