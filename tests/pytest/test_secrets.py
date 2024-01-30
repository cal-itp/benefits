import pytest

from benefits.secrets import KEY_VAULT_URL, get_secret_by_name


@pytest.fixture(autouse=True)
def mock_DefaultAzureCredential(mocker):
    # patching the class to ensure new instances always return the same mock
    credential_cls = mocker.patch("benefits.secrets.DefaultAzureCredential")
    credential_cls.return_value = mocker.Mock()
    return credential_cls


def test_get_secret_by_name__with_client__returns_value(mocker):
    secret_name = "the secret name"
    secret_value = "the secret value"
    client = mocker.patch("benefits.secrets.SecretClient")
    client.get_secret.return_value = mocker.Mock(value=secret_value)

    actual_value = get_secret_by_name(secret_name, client)

    client.get_secret.assert_called_once_with(secret_name)
    assert actual_value == secret_value


def test_get_secret_by_name__None_client__returns_value(mocker, settings, mock_DefaultAzureCredential):
    secret_name = "the secret name"
    secret_value = "the secret value"

    # override runtime to dev
    settings.RUNTIME_ENVIRONMENT = lambda: "dev"
    expected_keyvault_url = KEY_VAULT_URL.format(env="d")

    # set up the mock client class and expected return values
    # this test does not pass in a known client, instead checking that a client is constructed as expected
    mock_credential = mock_DefaultAzureCredential.return_value
    client_cls = mocker.patch("benefits.secrets.SecretClient")
    client = client_cls.return_value
    client.get_secret.return_value = mocker.Mock(value=secret_value)

    actual_value = get_secret_by_name(secret_name)

    client_cls.assert_called_once_with(vault_url=expected_keyvault_url, credential=mock_credential)
    client.get_secret.assert_called_once_with(secret_name)
    assert actual_value == secret_value
