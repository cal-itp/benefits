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


@pytest.mark.django_db
def test_instance_scope():
    scope1 = "scope1"
    oauth_client = client.instance(scope1)
    client_scope = oauth_client.client_kwargs["scope"]

    assert scope1 in client_scope
    assert client._OPENID_SCOPE in client_scope

    scope2 = "scope2"
    oauth_client2 = client.instance(scope2)
    client_scope = oauth_client2.client_kwargs["scope"]

    assert scope1 not in client_scope
    assert scope2 in client_scope
    assert client._OPENID_SCOPE in client_scope

    scope3 = " ".join((scope1, scope2))
    oauth_client3 = client.instance(scope3)
    client_scope = oauth_client3.client_kwargs["scope"]

    assert scope1 in client_scope
    assert scope2 in client_scope
    assert scope3 in client_scope
    assert client._OPENID_SCOPE in client_scope
