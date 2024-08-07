from django.http import HttpResponse
from django.urls import reverse

import pytest

from benefits.core import session
from benefits.core.middleware import ROUTE_INDEX, TEMPLATE_USER_ERROR

from benefits.eligibility.views import ROUTE_START

from benefits.oauth.redirects import ROUTE_SYSTEM_ERROR
from benefits.oauth.views import (
    ROUTE_CONFIRM,
    ROUTE_UNVERIFIED,
    TEMPLATE_SYSTEM_ERROR,
    _oauth_client_or_error_redirect,
    login,
    authorize,
    cancel,
    logout,
    post_logout,
    system_error,
)
import benefits.oauth.views


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.views)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.oauth.views, "sentry_sdk")


@pytest.fixture
def mocked_oauth_client_or_error_redirect__client(mocked_oauth_create_client):
    mocked_oauth_create_client.return_value.authorize_redirect.return_value = HttpResponse("authorize redirect")
    mocked_oauth_create_client.return_value.authorize_access_token.return_value = HttpResponse("authorize access token")
    mocked_oauth_create_client.return_value.load_server_metadata.return_value = HttpResponse("load server metadata")
    return mocked_oauth_create_client


@pytest.fixture
def mocked_oauth_client_or_error_redirect__error(mocked_oauth_create_client):
    mocked_oauth_create_client.side_effect = Exception("Side effect")
    return mocked_oauth_create_client


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_oauth_client_or_error_redirect_no_oauth_client(
    app_request,
    model_EnrollmentFlow_with_scope_and_claim,
    mocked_oauth_create_client,
    mocked_analytics_module,
    mocked_sentry_sdk_module,
):
    mocked_oauth_create_client.return_value = None

    result = _oauth_client_or_error_redirect(app_request, model_EnrollmentFlow_with_scope_and_claim)

    assert result.status_code == 302
    assert result.url == reverse(ROUTE_SYSTEM_ERROR)
    mocked_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification", "mocked_oauth_client_or_error_redirect__error")
def test_oauth_client_or_error_redirect_oauth_client_exception(
    app_request, model_EnrollmentFlow_with_scope_and_claim, mocked_analytics_module, mocked_sentry_sdk_module
):
    result = _oauth_client_or_error_redirect(app_request, model_EnrollmentFlow_with_scope_and_claim)

    assert result.status_code == 302
    assert result.url == reverse(ROUTE_SYSTEM_ERROR)
    mocked_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification", "mocked_oauth_create_client")
def test_oauth_client_or_error_oauth_client(
    app_request, model_EnrollmentFlow_with_scope_and_claim, mocked_analytics_module, mocked_sentry_sdk_module
):
    result = _oauth_client_or_error_redirect(app_request, model_EnrollmentFlow_with_scope_and_claim)

    assert hasattr(result, "authorize_redirect")
    mocked_analytics_module.error.assert_not_called()
    mocked_sentry_sdk_module.capture_exception.assert_not_called()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification", "mocked_oauth_client_or_error_redirect__error")
def test_login_oauth_client_init_error(app_request, mocked_analytics_module):
    result = login(app_request)

    assert result.status_code == 302
    assert result.url == reverse(ROUTE_SYSTEM_ERROR)
    mocked_analytics_module.error.assert_called_once()


@pytest.mark.django_db
def test_login_no_session_flow(app_request):
    result = login(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_login(app_request, mocked_oauth_client_or_error_redirect__client, mocked_analytics_module):
    assert not session.logged_in(app_request)
    mocked_oauth_client = mocked_oauth_client_or_error_redirect__client.return_value
    # fake a permanent redirect response from the client
    mocked_oauth_client.authorize_redirect.return_value.status_code = 301

    login(app_request)

    mocked_oauth_client.authorize_redirect.assert_called_with(app_request, "https://testserver/oauth/authorize")
    mocked_analytics_module.started_sign_in.assert_called_once()
    assert not session.logged_in(app_request)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_login_authorize_redirect_exception(
    app_request, mocked_oauth_client_or_error_redirect__client, mocked_analytics_module, mocked_sentry_sdk_module
):
    mocked_oauth_client = mocked_oauth_client_or_error_redirect__client.return_value
    mocked_oauth_client.authorize_redirect.side_effect = Exception("Side effect")

    result = login(app_request)

    assert result.status_code == 302
    assert result.url == reverse(ROUTE_SYSTEM_ERROR)
    mocked_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
@pytest.mark.parametrize("status_code", [400, 401, 403, 404, 500, 501, 503])
def test_login_authorize_redirect_error_response(
    app_request, mocked_oauth_client_or_error_redirect__client, mocked_analytics_module, mocked_sentry_sdk_module, status_code
):
    mocked_oauth_client = mocked_oauth_client_or_error_redirect__client.return_value
    mocked_oauth_client.authorize_redirect.return_value.status_code = status_code

    result = login(app_request)

    assert result.status_code == 302
    assert result.url == reverse(ROUTE_SYSTEM_ERROR)
    mocked_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification", "mocked_oauth_client_or_error_redirect__error")
def test_authorize_oauth_client_init_error(app_request, mocked_analytics_module, mocked_sentry_sdk_module):
    result = authorize(app_request)

    assert result.status_code == 302
    assert result.url == reverse(ROUTE_SYSTEM_ERROR)
    mocked_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
def test_authorize_no_session_flow(app_request):
    result = authorize(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_authorize_error(
    mocked_oauth_client_or_error_redirect__client, mocked_analytics_module, mocked_sentry_sdk_module, app_request
):
    mocked_oauth_client = mocked_oauth_client_or_error_redirect__client.return_value
    mocked_oauth_client.authorize_access_token.side_effect = Exception("Side effect")

    assert not session.logged_in(app_request)

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert not session.logged_in(app_request)
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_SYSTEM_ERROR)
    mocked_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_authorize_empty_token(
    mocked_oauth_client_or_error_redirect__client, mocked_analytics_module, mocked_sentry_sdk_module, app_request
):
    mocked_oauth_client = mocked_oauth_client_or_error_redirect__client.return_value
    mocked_oauth_client.authorize_access_token.return_value = None

    assert not session.logged_in(app_request)

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert not session.logged_in(app_request)
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_SYSTEM_ERROR)
    mocked_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_authorize_success(mocked_oauth_client_or_error_redirect__client, mocked_analytics_module, app_request):
    mocked_oauth_client = mocked_oauth_client_or_error_redirect__client.return_value
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
def test_authorize_success_with_claim_true(
    app_request, mocked_session_flow_uses_claims_verification, mocked_oauth_client_or_error_redirect__client
):
    flow = mocked_session_flow_uses_claims_verification.return_value
    flow.claims_claim = "claim"
    mocked_oauth_client = mocked_oauth_client_or_error_redirect__client.return_value
    mocked_oauth_client.authorize_access_token.return_value = {"id_token": "token", "userinfo": {"claim": "1"}}

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert session.oauth_claim(app_request) == "claim"
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_analytics_module")
def test_authorize_success_with_claim_false(
    app_request, mocked_session_flow_uses_claims_verification, mocked_oauth_client_or_error_redirect__client
):
    flow = mocked_session_flow_uses_claims_verification.return_value
    flow.claims_claim = "claim"
    mocked_oauth_client = mocked_oauth_client_or_error_redirect__client.return_value
    mocked_oauth_client.authorize_access_token.return_value = {"id_token": "token", "userinfo": {"claim": "0"}}

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert session.oauth_claim(app_request) is None
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
def test_authorize_success_with_claim_error(
    app_request,
    mocked_session_flow_uses_claims_verification,
    mocked_oauth_client_or_error_redirect__client,
    mocked_analytics_module,
):
    flow = mocked_session_flow_uses_claims_verification.return_value
    flow.claims_claim = "claim"
    mocked_oauth_client = mocked_oauth_client_or_error_redirect__client.return_value
    mocked_oauth_client.authorize_access_token.return_value = {"id_token": "token", "userinfo": {"claim": "10"}}

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    mocked_analytics_module.finished_sign_in.assert_called_with(app_request, error=10)
    assert session.oauth_claim(app_request) is None
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_analytics_module")
def test_authorize_success_without_flow_claim(
    app_request, mocked_session_flow_uses_claims_verification, mocked_oauth_client_or_error_redirect__client
):
    flow = mocked_session_flow_uses_claims_verification.return_value
    flow.claims_claim = ""
    mocked_oauth_client = mocked_oauth_client_or_error_redirect__client.return_value
    mocked_oauth_client.authorize_access_token.return_value = {"id_token": "token", "userinfo": {"claim": "1"}}

    result = authorize(app_request)

    assert session.oauth_claim(app_request) is None
    assert result.status_code == 200
    assert result.template_name == TEMPLATE_USER_ERROR


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
    app_request,
    mocked_session_flow_uses_claims_verification,
    mocked_oauth_client_or_error_redirect__client,
    access_token_response,
):
    flow = mocked_session_flow_uses_claims_verification.return_value
    flow.claims_claim = "claim"
    mocked_oauth_client = mocked_oauth_client_or_error_redirect__client.return_value
    mocked_oauth_client.authorize_access_token.return_value = access_token_response

    result = authorize(app_request)

    mocked_oauth_client.authorize_access_token.assert_called_with(app_request)
    assert session.oauth_claim(app_request) is None
    assert result.status_code == 302
    assert result.url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_cancel(app_request, mocked_analytics_module):
    unverified_route = reverse(ROUTE_UNVERIFIED)

    result = cancel(app_request)

    mocked_analytics_module.canceled_sign_in.assert_called_once()
    assert result.status_code == 302
    assert result.url == unverified_route


@pytest.mark.django_db
def test_cancel_no_session_flow(app_request):
    result = cancel(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification", "mocked_oauth_client_or_error_redirect__error")
def test_logout_oauth_client_init_error(app_request):
    result = authorize(app_request)

    assert result.status_code == 302
    assert result.url == reverse(ROUTE_SYSTEM_ERROR)


@pytest.mark.django_db
def test_logout_no_session_flow(app_request):
    result = logout(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_logout(app_request, mocker, mocked_oauth_client_or_error_redirect__client, mocked_analytics_module):
    # logout internally calls deauthorize_redirect
    # this mocks that function and a success response
    # and returns a spy object we can use to validate calls
    message = "logout successful"
    mocked_oauth_client = mocked_oauth_client_or_error_redirect__client.return_value
    mocked_redirect = mocker.patch("benefits.oauth.views.redirects.deauthorize_redirect", return_value=HttpResponse(message))

    token = "token"
    session.update(app_request, oauth_token=token)
    assert session.oauth_token(app_request) == token

    result = logout(app_request)

    mocked_redirect.assert_called_with(app_request, mocked_oauth_client, token, "https://testserver/oauth/post_logout")
    mocked_analytics_module.started_sign_out.assert_called_once()
    assert result.status_code == 200
    assert message in str(result.content)

    assert not session.logged_in(app_request)
    assert session.enrollment_token(app_request) is False
    assert session.oauth_token(app_request) is False
    assert session.oauth_claim(app_request) is False


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_post_logout(app_request, mocked_analytics_module):
    origin = reverse(ROUTE_INDEX)
    session.update(app_request, origin=origin)

    result = post_logout(app_request)

    assert result.status_code == 302
    assert result.url == origin
    mocked_analytics_module.finished_sign_out.assert_called_once()


@pytest.mark.django_db
def test_post_logout_no_session_flow(app_request):
    result = post_logout(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_system_error(app_request, model_TransitAgency):
    origin = reverse(ROUTE_START)
    session.update(app_request, origin=origin)

    result = system_error(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_SYSTEM_ERROR
    assert session.origin(app_request) == model_TransitAgency.index_url


@pytest.mark.django_db
def test_system_error_no_agency(app_request):
    result = system_error(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_USER_ERROR
