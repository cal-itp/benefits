from authlib.integrations.django_client.apps import DjangoOAuth2App

import pytest


@pytest.fixture
def mocked_oauth_client(mocker):
    mock_client = mocker.Mock(spec=DjangoOAuth2App)
    mocker.patch("benefits.oauth.client.instance", return_value=mock_client)
    return mock_client
