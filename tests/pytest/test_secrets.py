import pytest

from benefits.secrets import KEY_VAULT_URL, get_secret_by_name


@pytest.fixture(autouse=True)
def mock_DefaultAzureCredential(mocker):
    # patching the class to ensure new instances always return the same mock
    credential_cls = mocker.patch("benefits.secrets.DefaultAzureCredential")
    credential_cls.return_value = mocker.Mock()
    return credential_cls


@pytest.mark.parametrize("runtime_env", ["dev", "test", "prod"])
def test_get_secret_by_name__with_client__returns_secret_value(mocker, runtime_env, settings):
    settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

    # set up the mock client class and expected return values

    secret_name = "the secret name"
    secret_value = "the secret value"
    client = mocker.patch("benefits.secrets.SecretClient")
    client.get_secret.return_value = mocker.Mock(value=secret_value)

    actual_value = get_secret_by_name(secret_name, client)

    client.get_secret.assert_called_once_with(secret_name)
    assert actual_value == secret_value


@pytest.mark.parametrize("runtime_env", ["dev", "test", "prod"])
def test_get_secret_by_name__None_client__returns_secret_value(mocker, runtime_env, settings, mock_DefaultAzureCredential):
    settings.RUNTIME_ENVIRONMENT = lambda: runtime_env
    expected_keyvault_url = KEY_VAULT_URL.format(env=runtime_env[0])

    # set up the mock client class and expected return values
    # this test does not pass in a known client, instead checking that a client is constructed as expected

    secret_name = "the secret name"
    secret_value = "the secret value"

    mock_credential = mock_DefaultAzureCredential.return_value
    client_cls = mocker.patch("benefits.secrets.SecretClient")
    client = client_cls.return_value
    client.get_secret.return_value = mocker.Mock(value=secret_value)

    actual_value = get_secret_by_name(secret_name)

    client_cls.assert_called_once_with(vault_url=expected_keyvault_url, credential=mock_credential)
    client.get_secret.assert_called_once_with(secret_name)
    assert actual_value == secret_value


def test_get_secret_by_name__local__returns_environment_variable(mocker, settings):
    settings.RUNTIME_ENVIRONMENT = lambda: "local"

    secret_name = "the secret name"
    secret_value = "the secret value"

    env_spy = mocker.patch("benefits.secrets.os.environ.get", return_value=secret_value)
    client_cls = mocker.patch("benefits.secrets.SecretClient")
    client = client_cls.return_value

    actual_value = get_secret_by_name(secret_name)

    client_cls.assert_not_called()
    client.get_secret.assert_not_called()
    env_spy.assert_called_once_with(secret_name)
    assert actual_value == secret_value
