from cdt_identity.claims import ClaimsResult
from cdt_identity.hooks import Operation
from cdt_identity.models import ClaimsVerificationRequest
from django.urls import reverse
import pytest

import benefits.eligibility
import benefits.eligibility.views
from benefits.routes import routes
from benefits.oauth.hooks import OAuthHooks
import benefits.oauth.hooks
from benefits.core import session


@pytest.fixture
def mocked_oauth_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.hooks)


@pytest.fixture
def mocked_eligibility_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.eligibility.views)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.oauth.hooks, "sentry_sdk")


def test_pre_login(app_request, mocked_oauth_analytics_module):
    OAuthHooks.pre_login(app_request)

    mocked_oauth_analytics_module.started_sign_in.assert_called_once()


def test_cancel_login(app_request, mocked_oauth_analytics_module):
    result = OAuthHooks.cancel_login(app_request)

    assert result.status_code == 302
    assert result.url == reverse(routes.ELIGIBILITY_UNVERIFIED)
    mocked_oauth_analytics_module.canceled_sign_in.assert_called_once_with(app_request)


def test_pre_logout(app_request, mocked_oauth_analytics_module):
    session.update(app_request, oauth_authorized=True)
    assert session.logged_in(app_request)

    OAuthHooks.pre_logout(app_request)

    mocked_oauth_analytics_module.started_sign_out.assert_called_once_with(app_request)
    assert not session.logged_in(app_request)


@pytest.mark.parametrize("origin", [routes.ELIGIBILITY_START, routes.INDEX])
def test_post_logout(app_request, mocked_oauth_analytics_module, origin):
    session.update(app_request, origin=origin)

    result = OAuthHooks.post_logout(app_request)

    assert result.status_code == 302
    assert result.url == reverse(origin)
    mocked_oauth_analytics_module.finished_sign_out.assert_called_once_with(app_request)


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_session_agency", "mocked_session_flow_uses_claims_verification", "mocked_session_oauth_authorized"
)
def test_claims_verified_eligible(
    app_request, mocked_oauth_analytics_module, mocked_session_update, mocked_eligibility_analytics_module
):
    result = OAuthHooks.claims_verified_eligible(app_request, ClaimsVerificationRequest(), ClaimsResult())

    assert result.status_code == 302
    assert result.url == reverse(routes.ENROLLMENT_INDEX)
    mocked_oauth_analytics_module.finished_sign_in.assert_called_once_with(app_request)
    mocked_session_update.assert_any_call(app_request, oauth_authorized=True)
    mocked_session_update.assert_any_call(app_request, eligible=True)
    mocked_eligibility_analytics_module.returned_success.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_session_agency", "mocked_session_flow_uses_claims_verification", "mocked_session_oauth_authorized"
)
def test_claims_verified_not_eligible(app_request, mocked_oauth_analytics_module, mocked_session_update):
    claims_result = ClaimsResult(errors={"some_claim": "error message"})
    result = OAuthHooks.claims_verified_not_eligible(app_request, ClaimsVerificationRequest(), claims_result)

    assert result.status_code == 302
    assert result.url == reverse(routes.ELIGIBILITY_UNVERIFIED)
    mocked_session_update.assert_called_once_with(app_request, oauth_authorized=True)
    mocked_oauth_analytics_module.finished_sign_in.assert_called_once_with(app_request, error=claims_result.errors)


@pytest.mark.parametrize("operation", Operation)
def test_system_error(app_request, mocked_oauth_analytics_module, mocked_sentry_sdk_module, operation):
    result = OAuthHooks.system_error(app_request, Exception("some exception"), operation)

    assert result.status_code == 302
    assert result.url == reverse(routes.OAUTH_SYSTEM_ERROR)
    mocked_oauth_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()
