import pytest

import benefits.oauth.client as client


@pytest.fixture
def no_oauth_client_name(mocker):
    return mocker.patch("benefits.oauth.client.settings.OAUTH_CLIENT_NAME", None)


@pytest.mark.django_db
@pytest.mark.usefixtures("no_oauth_client_name")
def test_instance_no_oauth_client_name():
    with pytest.raises(Exception, match=r"OAUTH_CLIENT_NAME"):
        client.instance()


@pytest.mark.django_db
def test_instance_oauth_client_name():
    assert not client._OAUTH_CLIENT

    oauth_client = client.instance()

    assert oauth_client
    assert client._OAUTH_CLIENT is oauth_client

    oauth_client2 = client.instance()

    assert oauth_client is oauth_client2
