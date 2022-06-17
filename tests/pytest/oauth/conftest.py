from authlib.integrations.django_client import OAuth
from authlib.integrations.django_client.apps import DjangoOAuth2App

import pytest


@pytest.fixture
def mocked_oauth_registry(mocker):
    return mocker.Mock(spec=OAuth)


@pytest.fixture
def mocked_oauth_client_registry(mocker, mocked_oauth_registry):
    return mocker.patch("benefits.oauth.client.oauth", mocked_oauth_registry)


@pytest.fixture
def mocked_oauth_client(mocker):
    return mocker.Mock(spec=DjangoOAuth2App)


@pytest.fixture
def mocked_oauth_client_instance(mocker, mocked_oauth_client):
    return mocker.patch("benefits.oauth.client.instance", return_value=mocked_oauth_client)
