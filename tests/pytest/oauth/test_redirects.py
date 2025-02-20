from django.urls import reverse

import pytest

from benefits.oauth.redirects import deauthorize_redirect, generate_redirect_uri
import benefits.oauth.redirects
from benefits.routes import routes


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.oauth.redirects)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.oauth.redirects, "sentry_sdk")


def test_deauthorize_redirect(app_request, mocked_oauth_client):
    mocked_oauth_client.client_id = "test-client-id"
    mocked_oauth_client.load_server_metadata.return_value = {"end_session_endpoint": "https://server/endsession"}

    result = deauthorize_redirect(app_request, mocked_oauth_client, "https://localhost/redirect_uri")

    mocked_oauth_client.load_server_metadata.assert_called()
    assert result.status_code == 302
    assert (
        result.url
        == "https://server/endsession?client_id=test-client-id&post_logout_redirect_uri=https%3A%2F%2Flocalhost%2Fredirect_uri"
    )


@pytest.mark.django_db
def test_deauthorize_redirect_load_server_metadata_error(
    app_request, mocked_oauth_client, mocked_analytics_module, mocked_sentry_sdk_module
):
    mocked_oauth_client.load_server_metadata.side_effect = Exception("Side effect")

    result = deauthorize_redirect(app_request, mocked_oauth_client, "https://localhost/redirect_uri")

    assert result.status_code == 302
    assert result.url == reverse(routes.OAUTH_SYSTEM_ERROR)
    mocked_analytics_module.error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


def test_generate_redirect_uri_default(rf):
    request = rf.get("/oauth/login")
    path = "/test"

    redirect_uri = generate_redirect_uri(request, path)

    assert redirect_uri == "https://testserver/test"


def test_generate_redirect_uri_localhost(rf):
    request = rf.get("/oauth/login", SERVER_NAME="localhost")
    path = "/test"

    redirect_uri = generate_redirect_uri(request, path)

    assert redirect_uri == "http://localhost/test"
