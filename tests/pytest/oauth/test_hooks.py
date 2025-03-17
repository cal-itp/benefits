from django.urls import reverse

import pytest

from benefits.routes import routes
from benefits.oauth.hooks import OAuthHooks
import benefits.oauth.hooks


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.hooks)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.oauth.hooks, "sentry_sdk")


def test_pre_login(app_request, mocked_analytics_module):
    OAuthHooks.pre_login(app_request)

    mocked_analytics_module.started_sign_in.assert_called_once()


def test_system_error(app_request, mocked_analytics_module, mocked_sentry_sdk_module):
    result = OAuthHooks.system_error(app_request, Exception("some exception"))

    assert result.status_code == 302
    assert result.url == reverse(routes.OAUTH_SYSTEM_ERROR)
    mocked_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()
