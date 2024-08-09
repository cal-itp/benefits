import pytest

from benefits.core.models import EligibilityVerifier
from benefits.oauth.client import _client_kwargs, _server_metadata_url, _authorize_params, _register_provider, create_client


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
def test_register_provider(mocker, mocked_oauth_registry):
    mocked_client_provider = mocker.Mock(spec=EligibilityVerifier)
    mocked_client_provider.claims_provider.client_name = "client_name_1"
    mocked_client_provider.claims_provider.client_id = "client_id_1"

    mocker.patch("benefits.oauth.client._client_kwargs", return_value={"client": "kwargs"})
    mocker.patch("benefits.oauth.client._server_metadata_url", return_value="https://metadata.url")
    mocker.patch("benefits.oauth.client._authorize_params", return_value={"scheme": "test_scheme"})

    _register_provider(mocked_oauth_registry, mocked_client_provider)

    mocked_oauth_registry.register.assert_any_call(
        "client_name_1",
        client_id="client_id_1",
        server_metadata_url="https://metadata.url",
        client_kwargs={"client": "kwargs"},
        authorize_params={"scheme": "test_scheme"},
    )


@pytest.mark.django_db
def test_create_client_already_registered(mocker, mocked_oauth_registry):
    mocked_client_provider = mocker.Mock(spec=EligibilityVerifier)
    mocked_client_provider.claims_provider.client_name = "client_name_1"
    mocked_client_provider.claims_provider.client_id = "client_id_1"

    create_client(mocked_oauth_registry, mocked_client_provider)

    mocked_oauth_registry.create_client.assert_any_call("client_name_1")
    mocked_oauth_registry.register.assert_not_called()


@pytest.mark.django_db
def test_create_client_already_not_registered_yet(mocker, mocked_oauth_registry):
    mocked_client_provider = mocker.Mock(spec=EligibilityVerifier)
    mocked_client_provider.claims_provider.client_name = "client_name_1"
    mocked_client_provider.claims_provider.client_id = "client_id_1"

    mocker.patch("benefits.oauth.client._client_kwargs", return_value={"client": "kwargs"})
    mocker.patch("benefits.oauth.client._server_metadata_url", return_value="https://metadata.url")
    mocker.patch("benefits.oauth.client._authorize_params", return_value={"scheme": "test_scheme"})

    mocked_oauth_registry.create_client.return_value = None

    create_client(mocked_oauth_registry, mocked_client_provider)

    mocked_oauth_registry.create_client.assert_any_call("client_name_1")
    mocked_oauth_registry.register.assert_any_call(
        "client_name_1",
        client_id="client_id_1",
        server_metadata_url="https://metadata.url",
        client_kwargs={"client": "kwargs"},
        authorize_params={"scheme": "test_scheme"},
    )
