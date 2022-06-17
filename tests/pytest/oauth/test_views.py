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


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_login(mocked_oauth_client_instance, mocked_analytics_module, app_request):
    assert not session.logged_in(app_request)

    mocked_oauth_client = mocked_oauth_client_instance.return_value
    mocked_oauth_client.authorize_redirect.return_value = HttpResponse("authorize redirect")

    login(app_request)

    mocked_oauth_client.authorize_redirect.assert_called_with(app_request, "https://testserver/oauth/authorize")
    mocked_analytics_module.started_sign_in.assert_called_once()
    assert not session.logged_in(app_request)


@pytest.mark.django_db
def test_login_scope(mocked_oauth_client_instance, mocked_session_verifier_auth_required, app_request):
    mocked_oauth_client = mocked_oauth_client_instance.return_value
    mocked_oauth_client.authorize_redirect.return_value = HttpResponse("authorize redirect")

    mocked_verifier = mocked_session_verifier_auth_required.return_value
    mocked_verifier.auth_provider.scope = "scope"

    login(app_request)

    mocked_oauth_client_instance.assert_called_once_with(mocked_verifier.auth_provider.scope)


def test_authorize_fail(mocked_oauth_client_instance, app_request):
    mocked_oauth_client = mocked_oauth_client_instance.return_value
    mocked_oauth_client.authorize_access_token.return_value = None

    assert not session.logged_in(app_request)

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert not session.logged_in(app_request)
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_START)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_authorize_success(mocked_oauth_client_instance, mocked_analytics_module, app_request):
    mocked_oauth_client = mocked_oauth_client_instance.return_value
    mocked_oauth_client.authorize_access_token.return_value = {"id_token": "token"}

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    mocked_analytics_module.finished_sign_in.assert_called_once()
    assert session.logged_in(app_request)
    assert session.oauth_token(app_request) == "token"
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
def test_authorize_success_with_claim(mocked_session_verifier_auth_required, mocked_oauth_client_instance, app_request):
    verifier = mocked_session_verifier_auth_required.return_value
    verifier.auth_provider.claim = "claim"
    mocked_oauth_client = mocked_oauth_client_instance.return_value
    mocked_oauth_client.authorize_access_token.return_value = {"id_token": "token", "userinfo": {"claim": "True"}}

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert session.oauth_claim(app_request) == "claim"
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
def test_authorize_success_without_claim(mocked_session_verifier_auth_required, mocked_oauth_client_instance, app_request):
    # mocked_session_verifier_auth_required is a fixture that mocks benefits.core.session.verifier(request)
    # call it here, passing a None request, to get the return value from the mock
    verifier = mocked_session_verifier_auth_required(None)
    verifier.auth_claim = ""
    mocked_oauth_client = mocked_oauth_client_instance.return_value
    mocked_oauth_client.authorize_access_token.return_value = {"id_token": "token", "userinfo": {"claim": "True"}}

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert session.oauth_claim(app_request) is None
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


def test_logout(mocker, mocked_analytics_module, app_request):
    # logout internally calls deauthorize_redirect
    # this mocks that function and a success response
    # and returns a spy object we can use to validate calls
    message = "logout successful"
    spy = mocker.patch("benefits.oauth.views.redirects.deauthorize_redirect", return_value=HttpResponse(message))

    token = "token"
    session.update(app_request, oauth_token=token)
    assert session.oauth_token(app_request) == token

    result = logout(app_request)

    spy.assert_called_with(token, "https://testserver/oauth/post_logout")
    mocked_analytics_module.started_sign_out.assert_called_once()
    assert result.status_code == 200
    assert message in str(result.content)
    assert not session.logged_in(app_request)
    assert session.enrollment_token(app_request) is False


def test_post_logout(app_request, mocked_analytics_module):
    origin = reverse(ROUTE_INDEX)
    session.update(app_request, origin=origin)

    result = post_logout(app_request)

    assert result.status_code == 302
    assert result.url == origin
    mocked_analytics_module.finished_sign_out.assert_called_once()
