import pytest
from cdt_identity.claims import ClaimsResult
from cdt_identity.models import ClaimsVerificationRequest
from cdt_identity.session import Session as OAuthSession
from django.urls import reverse

import benefits.eligibility
import benefits.eligibility.views
import benefits.oauth.hooks
from benefits.core import session
from benefits.metro_mobility_wallet.oauth import OAuthHooks

# from benefits.routes import routes


@pytest.fixture
def mocked_oauth_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.hooks)


@pytest.fixture
def mocked_eligibility_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.eligibility.views)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.metro_mobility_wallet.oauth, "sentry_sdk")


def test_pre_login(app_request, mocked_oauth_analytics_module):
    OAuthHooks.pre_login(app_request)

    # mocked_oauth_analytics_module.started_sign_in.assert_called_once()


def test_pre_logout(app_request, mocked_oauth_analytics_module):
    session.update(app_request, logged_in=True)
    assert session.logged_in(app_request)

    OAuthHooks.pre_logout(app_request)

    # mocked_oauth_analytics_module.started_sign_out.assert_called_once_with(app_request)
    assert not session.logged_in(app_request)
    assert session.logged_in(app_request) is False
    assert OAuthSession(app_request).claims_result == ClaimsResult()


@pytest.mark.django_db
def test_claims_verified_eligible(app_request, mocked_oauth_analytics_module, mocked_session_update):
    assert app_request.method == "GET"

    response = OAuthHooks.claims_verified_eligible(app_request, ClaimsVerificationRequest(), ClaimsResult())

    assert response.status_code == 302
    assert response.url == reverse("metro_mobility_wallet:confirmation")

    # mocked_oauth_analytics_module.finished_sign_in.assert_called_once_with(app_request)
    mocked_session_update.assert_any_call(app_request, logged_in=True)
    mocked_session_update.assert_any_call(app_request, eligible=True)
