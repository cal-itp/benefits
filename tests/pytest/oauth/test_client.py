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
def test_instance():
    oauth_client = client.instance()
    oauth_client2 = client.instance()

    assert oauth_client
    assert oauth_client2
    assert oauth_client is not oauth_client2
