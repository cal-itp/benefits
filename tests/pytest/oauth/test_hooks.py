import pytest

from benefits.oauth.hooks import OAuthHooks
import benefits.oauth.hooks


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.hooks)


def test_pre_login(app_request, mocked_analytics_module):
    OAuthHooks.pre_login(app_request)

    mocked_analytics_module.started_sign_in.assert_called_once()
