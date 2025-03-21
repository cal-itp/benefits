from cdt_identity.hooks import Operation
from django.urls import reverse
import pytest

from benefits.routes import routes
from benefits.oauth.hooks import OAuthHooks
import benefits.oauth.hooks
from benefits.core import session


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.hooks)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.oauth.hooks, "sentry_sdk")


def test_pre_login(app_request, mocked_analytics_module):
    OAuthHooks.pre_login(app_request)

    mocked_analytics_module.started_sign_in.assert_called_once()


def test_cancel_login(app_request, mocked_analytics_module):
    result = OAuthHooks.cancel_login(app_request)

    assert result.status_code == 302
    assert result.url == reverse(routes.ELIGIBILITY_UNVERIFIED)
    mocked_analytics_module.canceled_sign_in.assert_called_once_with(app_request)


def test_pre_logout(app_request, mocked_analytics_module):
    session.update(app_request, oauth_authorized=True)
    assert session.logged_in(app_request)

    OAuthHooks.pre_logout(app_request)

    mocked_analytics_module.started_sign_out.assert_called_once_with(app_request)
    assert not session.logged_in(app_request)


@pytest.mark.parametrize("origin", [routes.ELIGIBILITY_START, routes.INDEX])
def test_post_logout(app_request, mocked_analytics_module, origin):
    session.update(app_request, origin=origin)

    result = OAuthHooks.post_logout(app_request)

    assert result.status_code == 302
    assert result.url == reverse(origin)
    mocked_analytics_module.finished_sign_out.assert_called_once_with(app_request)


@pytest.mark.parametrize("operation", Operation)
def test_system_error(app_request, mocked_analytics_module, mocked_sentry_sdk_module, operation):
    result = OAuthHooks.system_error(app_request, Exception("some exception"), operation)

    assert result.status_code == 302
    assert result.url == reverse(routes.OAUTH_SYSTEM_ERROR)
    mocked_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()
