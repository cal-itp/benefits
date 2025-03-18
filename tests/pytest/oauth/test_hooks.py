from cdt_identity.hooks import Operation
from django.urls import reverse
import pytest

from benefits.routes import routes
from benefits.oauth.hooks import OAuthHooks
import benefits.oauth.hooks
from cdt_identity.models import ClaimsVerificationRequest
from cdt_identity.claims import ClaimsResult


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.hooks)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.oauth.hooks, "sentry_sdk")


def test_pre_login(app_request, mocked_analytics_module):
    OAuthHooks.pre_login(app_request)

    mocked_analytics_module.started_sign_in.assert_called_once()


def test_claims_verified_eligible(app_request, mocked_analytics_module):
    result = OAuthHooks.claims_verified_eligible(app_request, ClaimsVerificationRequest(), ClaimsResult())

    assert result.status_code == 302
    assert result.url == reverse(routes.ELIGIBILITY_CONFIRM)
    mocked_analytics_module.finished_sign_in.assert_called_once_with(app_request)


def test_claims_verified_not_eligible(app_request, mocked_analytics_module):
    claims_result = ClaimsResult(errors={"some_claim": "error message"})
    result = OAuthHooks.claims_verified_not_eligible(app_request, ClaimsVerificationRequest(), claims_result)

    assert result.status_code == 302
    assert result.url == reverse(routes.ELIGIBILITY_CONFIRM)
    mocked_analytics_module.finished_sign_in.assert_called_once_with(app_request, error=claims_result.errors)


@pytest.mark.parametrize("operation", Operation)
def test_system_error(app_request, mocked_analytics_module, mocked_sentry_sdk_module, operation):
    result = OAuthHooks.system_error(app_request, Exception("some exception"), operation)

    assert result.status_code == 302
    assert result.url == reverse(routes.OAUTH_SYSTEM_ERROR)
    mocked_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()
