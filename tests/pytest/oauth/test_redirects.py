from django.urls import reverse


from benefits.oauth.redirects import ROUTE_SYSTEM_ERROR, deauthorize_redirect, generate_redirect_uri
import benefits.oauth.redirects

import pytest


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.oauth.redirects, "sentry_sdk")


def test_deauthorize_redirect(mocked_oauth_client):
    mocked_oauth_client.load_server_metadata.return_value = {"end_session_endpoint": "https://server/endsession"}

    result = deauthorize_redirect(mocked_oauth_client, "token", "https://localhost/redirect_uri")

    mocked_oauth_client.load_server_metadata.assert_called()
    assert result.status_code == 302
    assert (
        result.url
        == "https://server/endsession?id_token_hint=token&post_logout_redirect_uri=https%3A%2F%2Flocalhost%2Fredirect_uri"
    )


def test_deauthorize_redirect_load_server_metadata_error(mocked_oauth_client, mocked_sentry_sdk_module):
    mocked_oauth_client.load_server_metadata.side_effect = Exception("Side effect")

    result = deauthorize_redirect(mocked_oauth_client, "token", "https://localhost/redirect_uri")

    assert result.status_code == 302
    assert result.url == reverse(ROUTE_SYSTEM_ERROR)
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
