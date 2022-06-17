import benefits
from benefits.oauth.apps import OAuthAppConfig


def test_ready_registers_clients(mocker):
    mock_registry = mocker.patch("benefits.oauth.client.oauth")
    mock_register_providers = mocker.patch("benefits.oauth.client.register_providers")

    app = OAuthAppConfig("oauth", benefits)
    app.ready()

    mock_register_providers.assert_called_once_with(mock_registry)


def test_ready_register_exception(mocker):
    mocker.patch("benefits.oauth.client.oauth")
    mocker.patch("benefits.oauth.client.register_providers", side_effect=Exception)

    app = OAuthAppConfig("oauth", benefits)
    app.ready()

    # we expect no Exception to be raised
    assert app
