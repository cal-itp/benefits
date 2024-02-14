import pytest
from azure.core.exceptions import ClientAuthenticationError
from django.core.exceptions import ValidationError

from benefits.secrets import KEY_VAULT_URL, NAME_VALIDATOR, SecretNameValidator, get_secret_by_name


@pytest.fixture(autouse=True)
def mock_DefaultAzureCredential(mocker):
    # patching the class to ensure new instances always return the same mock
    credential_cls = mocker.patch("benefits.secrets.DefaultAzureCredential")
    credential_cls.return_value = mocker.Mock()
    return credential_cls


@pytest.fixture
def secret_name():
    return "the-secret-name"


@pytest.fixture
def secret_value():
    return "the secret value"


@pytest.mark.parametrize(
    "secret_name",
    [
        "a",
        "1",
        "one",
        "one-two-three",
        "1-2-3",
        "this-is-a-really-long-secret-name-in-fact-it-is-the-absolute-maximum-length-of-127-characters-to-be-exact-and-now-it-has-enough",  # noqa: E501
    ],
)
def test_SecretNameValidator_valid(secret_name):
    validator = SecretNameValidator()

    # a successful validation does not raise an Exception and returns None
    assert validator(secret_name) is None
    assert NAME_VALIDATOR(secret_name) is None


@pytest.mark.parametrize(
    "secret_name",
    [
        "",
        "!",
        "underscores_not_allowed",
        "this-is-a-really-long-secret-name-in-fact-it-much-much-longer-than-the-absolute-maximum-length-of-127-characters-and-now-it-has-enough-to-be-too-long",  # noqa: E501
    ],
)
def test_SecretNameValidator_invalid(secret_name):
    validator = SecretNameValidator()

    # an unsuccessful validation raises django.core.exceptions.ValidationError
    with pytest.raises(ValidationError):
        validator(secret_name)

    with pytest.raises(ValidationError):
        NAME_VALIDATOR(secret_name)


@pytest.mark.parametrize(
    "secret_name",
    [
        "",
        "!",
        "underscores_not_allowed",
        "this-is-a-really-long-secret-name-in-fact-it-much-much-longer-than-the-absolute-maximum-length-of-127-characters-and-now-it-has-enough-to-be-too-long",  # noqa: E501
    ],
)
def test_get_secret_by_name__invalid_name(secret_name):
    with pytest.raises(ValidationError):
        get_secret_by_name(secret_name)


@pytest.mark.parametrize("runtime_env", ["dev", "test", "prod"])
def test_get_secret_by_name__with_client__returns_secret_value(mocker, runtime_env, settings, secret_name, secret_value):
    settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

    client = mocker.patch("benefits.secrets.SecretClient")
    client.get_secret.return_value = mocker.Mock(value=secret_value)

    actual_value = get_secret_by_name(secret_name, client)

    client.get_secret.assert_called_once_with(secret_name)
    assert actual_value == secret_value


@pytest.mark.parametrize("runtime_env", ["dev", "test", "prod"])
def test_get_secret_by_name__None_client__returns_secret_value(
    mocker, runtime_env, settings, mock_DefaultAzureCredential, secret_name, secret_value
):
    settings.RUNTIME_ENVIRONMENT = lambda: runtime_env
    expected_keyvault_url = KEY_VAULT_URL.format(env=runtime_env[0])

    # this test does not pass in a known client, instead checking that a client is constructed as expected
    mock_credential = mock_DefaultAzureCredential.return_value
    client_cls = mocker.patch("benefits.secrets.SecretClient")
    client = client_cls.return_value
    client.get_secret.return_value = mocker.Mock(value=secret_value)

    actual_value = get_secret_by_name(secret_name)

    client_cls.assert_called_once_with(vault_url=expected_keyvault_url, credential=mock_credential)
    client.get_secret.assert_called_once_with(secret_name)
    assert actual_value == secret_value


@pytest.mark.parametrize("runtime_env", ["dev", "test", "prod"])
def test_get_secret_by_name__None_client__returns_None(mocker, runtime_env, settings, secret_name):
    settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

    # this test forces construction of a new client to None
    client_cls = mocker.patch("benefits.secrets.SecretClient", return_value=None)

    actual_value = get_secret_by_name(secret_name)

    client_cls.assert_called_once()
    assert actual_value is None


@pytest.mark.parametrize("runtime_env", ["dev", "test", "prod"])
def test_get_secret_by_name__unauthenticated_client__returns_None(mocker, runtime_env, settings, secret_name):
    settings.RUNTIME_ENVIRONMENT = lambda: runtime_env

    # this test forces client.get_secret to throw an exception
    client_cls = mocker.patch("benefits.secrets.SecretClient")
    client = client_cls.return_value
    client.get_secret.side_effect = ClientAuthenticationError

    actual_value = get_secret_by_name(secret_name)

    client_cls.assert_called_once()
    client.get_secret.assert_called_once_with(secret_name)
    assert actual_value is None


def test_get_secret_by_name__local__returns_environment_variable(mocker, settings, secret_name):
    settings.RUNTIME_ENVIRONMENT = lambda: "local"

    secret_value_literal_newlines = "the\\nsecret\\nvalue"
    expected_secret_value = secret_value_literal_newlines.replace("\\n", "\n")

    env_spy = mocker.patch("benefits.secrets.os.environ.get", return_value=secret_value_literal_newlines)
    env_secret_name = secret_name.replace("-", "_")
    client_cls = mocker.patch("benefits.secrets.SecretClient")
    client = client_cls.return_value

    actual_value = get_secret_by_name(secret_name)

    client_cls.assert_not_called()
    client.get_secret.assert_not_called()
    env_spy.assert_called_once_with(env_secret_name)
    assert actual_value == expected_secret_value
