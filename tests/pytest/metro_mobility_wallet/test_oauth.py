import pytest
from cdt_identity.claims import ClaimsResult
from cdt_identity.session import Session as OAuthSession

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
