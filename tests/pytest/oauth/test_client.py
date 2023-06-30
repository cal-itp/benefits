import pytest

from benefits.core.models import AuthProvider
from benefits.oauth.client import _client_kwargs, _server_metadata_url, _authorize_params, register_providers


def test_client_kwargs():
    kwargs = _client_kwargs()

    assert kwargs["code_challenge_method"] == "S256"
    assert kwargs["prompt"] == "login"
    assert "openid" in kwargs["scope"]


def test_client_kwargs_scope():
    kwargs = _client_kwargs("scope1")

    assert "openid" in kwargs["scope"]
    assert "scope1" in kwargs["scope"]


def test_server_metadata_url():
    url = _server_metadata_url("https://example.com")

    assert url.startswith("https://example.com")
    assert url.endswith("openid-configuration")


def test_authorize_params():
    params = _authorize_params("test_scheme")

    assert params == {"scheme": "test_scheme"}


def test_authorize_params_no_scheme():
    params = _authorize_params(None)

    assert params is None


@pytest.mark.django_db
def test_register_providers(mocker, mocked_oauth_registry):
    mock_providers = []

    for i in range(3):
        p = mocker.Mock(spec=AuthProvider)
        p.client_name = f"client_name_{i}"
        p.client_id = f"client_id_{i}"
        mock_providers.append(p)

    mocked_client_provider = mocker.patch("benefits.oauth.client.AuthProvider")
    mocked_client_provider.objects.all.return_value = mock_providers

    mocker.patch("benefits.oauth.client._client_kwargs", return_value={"client": "kwargs"})
    mocker.patch("benefits.oauth.client._server_metadata_url", return_value="https://metadata.url")
    mocker.patch("benefits.oauth.client._authorize_params", return_value={"scheme": "test_scheme"})

    register_providers(mocked_oauth_registry)

    mocked_client_provider.objects.all.assert_called_once()

    for provider in mock_providers:
        i = mock_providers.index(provider)

        mocked_oauth_registry.register.assert_any_call(
            f"client_name_{i}",
            client_id=f"client_id_{i}",
            server_metadata_url="https://metadata.url",
            client_kwargs={"client": "kwargs"},
            authorize_params={"scheme": "test_scheme"},
        )
