from django.http import HttpResponse
from django.urls import reverse

import pytest

from benefits.core import session
from benefits.core.middleware import ROUTE_INDEX, TEMPLATE_USER_ERROR

from benefits.oauth.views import ROUTE_START, ROUTE_CONFIRM, ROUTE_UNVERIFIED, login, authorize, cancel, logout, post_logout
import benefits.oauth.views


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.views)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_login_no_oauth_client(mocked_oauth_create_client, app_request):
    mocked_oauth_create_client.return_value = None

    with pytest.raises(Exception, match=r"oauth_client"):
        login(app_request)


@pytest.mark.django_db
def test_login_no_session_verifier(app_request):
    result = login(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
def test_login(mocked_oauth_create_client, mocked_session_verifier_auth_required, mocked_analytics_module, app_request):
    assert not session.logged_in(app_request)

    mocked_oauth_client = mocked_oauth_create_client.return_value
    mocked_oauth_client.authorize_redirect.return_value = HttpResponse("authorize redirect")

    login(app_request)

    mocked_verifier = mocked_session_verifier_auth_required.return_value
    mocked_oauth_create_client.assert_called_once_with(mocked_verifier.auth_provider.client_name)
    mocked_oauth_client.authorize_redirect.assert_called_with(app_request, "https://testserver/oauth/authorize")
    mocked_analytics_module.started_sign_in.assert_called_once()
    assert not session.logged_in(app_request)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_authorize_no_oauth_client(mocked_oauth_create_client, app_request):
    mocked_oauth_create_client.return_value = None

    with pytest.raises(Exception, match=r"oauth_client"):
        authorize(app_request)


@pytest.mark.django_db
def test_authorize_no_session_verifier(app_request):
    result = authorize(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_authorize_fail(mocked_oauth_create_client, app_request):
    mocked_oauth_client = mocked_oauth_create_client.return_value
    mocked_oauth_client.authorize_access_token.return_value = None

    assert not session.logged_in(app_request)

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert not session.logged_in(app_request)
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_START)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_authorize_success(mocked_oauth_create_client, mocked_analytics_module, app_request):
    mocked_oauth_client = mocked_oauth_create_client.return_value
    mocked_oauth_client.authorize_access_token.return_value = {"id_token": "token"}

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    mocked_analytics_module.finished_sign_in.assert_called_once()
    assert session.logged_in(app_request)
    assert session.oauth_token(app_request) == "token"
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_analytics_module")
@pytest.mark.parametrize("flag", ["true", "True", "tRuE"])
def test_authorize_success_with_claim_true(
    mocked_session_verifier_auth_required, mocked_oauth_create_client, app_request, flag
):
    verifier = mocked_session_verifier_auth_required.return_value
    verifier.auth_provider.claim = "claim"
    mocked_oauth_client = mocked_oauth_create_client.return_value
    mocked_oauth_client.authorize_access_token.return_value = {"id_token": "token", "userinfo": {"claim": flag}}

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert session.oauth_claim(app_request) == "claim"
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_analytics_module")
@pytest.mark.parametrize("flag", ["false", "False", "fAlSe"])
def test_authorize_success_with_claim_false(
    mocked_session_verifier_auth_required, mocked_oauth_create_client, app_request, flag
):
    verifier = mocked_session_verifier_auth_required.return_value
    verifier.auth_provider.claim = "claim"
    mocked_oauth_client = mocked_oauth_create_client.return_value
    mocked_oauth_client.authorize_access_token.return_value = {"id_token": "token", "userinfo": {"claim": flag}}

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert session.oauth_claim(app_request) is None
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_analytics_module")
def test_authorize_success_without_verifier_claim(
    mocked_session_verifier_auth_required, mocked_oauth_create_client, app_request
):
    verifier = mocked_session_verifier_auth_required.return_value
    verifier.auth_provider.claim = ""
    mocked_oauth_client = mocked_oauth_create_client.return_value
    mocked_oauth_client.authorize_access_token.return_value = {"id_token": "token", "userinfo": {"claim": "True"}}

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert session.oauth_claim(app_request) is None
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_analytics_module")
@pytest.mark.parametrize(
    "access_token_response",
    [
        {"id_token": "token"},  # no userinfo
        {"id_token": "token", "userinfo": {"something_unexpected": "True"}},  # has userinfo, but not the expected claim
    ],
)
def test_authorize_success_without_claim_in_response(
    mocked_session_verifier_auth_required, mocked_oauth_create_client, app_request, access_token_response
):
    verifier = mocked_session_verifier_auth_required.return_value
    verifier.auth_provider.claim = "claim"
    mocked_oauth_client = mocked_oauth_create_client.return_value
    mocked_oauth_client.authorize_access_token.return_value = access_token_response

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert session.oauth_claim(app_request) is None
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_cancel(mocked_analytics_module, app_request):
    unverified_route = reverse(ROUTE_UNVERIFIED)

    result = cancel(app_request)

    mocked_analytics_module.canceled_sign_in.assert_called_once()
    assert result.status_code == 302
    assert result.url == unverified_route


@pytest.mark.django_db
def test_cancel_no_session_verifier(app_request):
    result = cancel(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_logout_no_oauth_client(mocked_oauth_create_client, app_request):
    mocked_oauth_create_client.return_value = None

    with pytest.raises(Exception, match=r"oauth_client"):
        logout(app_request)


@pytest.mark.django_db
def test_logout_no_session_verifier(app_request):
    result = logout(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_logout(mocker, mocked_oauth_create_client, mocked_analytics_module, app_request):
    # logout internally calls deauthorize_redirect
    # this mocks that function and a success response
    # and returns a spy object we can use to validate calls
    message = "logout successful"
    mocked_oauth_client = mocked_oauth_create_client.return_value
    mocked_redirect = mocker.patch("benefits.oauth.views.redirects.deauthorize_redirect", return_value=HttpResponse(message))

    token = "token"
    session.update(app_request, oauth_token=token)
    assert session.oauth_token(app_request) == token

    result = logout(app_request)

    mocked_redirect.assert_called_with(mocked_oauth_client, token, "https://testserver/oauth/post_logout")
    mocked_analytics_module.started_sign_out.assert_called_once()
    assert result.status_code == 200
    assert message in str(result.content)

    assert not session.logged_in(app_request)
    assert session.enrollment_token(app_request) is False
    assert session.oauth_token(app_request) is False
    assert session.oauth_claim(app_request) is False


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier_auth_required")
def test_post_logout(app_request, mocked_analytics_module):
    origin = reverse(ROUTE_INDEX)
    session.update(app_request, origin=origin)

    result = post_logout(app_request)

    assert result.status_code == 302
    assert result.url == origin
    mocked_analytics_module.finished_sign_out.assert_called_once()


@pytest.mark.django_db
def test_post_logout_no_session_verifier(app_request):
    result = post_logout(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_USER_ERROR
