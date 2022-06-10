import time

from django.urls import reverse

import pytest


ROUTE_INDEX = "enrollment:index"
ROUTE_TOKEN = "enrollment:token"


@pytest.mark.django_db
def test_token_ineligibile(client):
    path = reverse(ROUTE_TOKEN)
    with pytest.raises(AttributeError, match=r"eligibility"):
        client.get(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_token_refresh(mocker, client):
    mocker.patch("benefits.core.session.enrollment_token_valid", return_value=False)

    mock_client = mocker.patch("benefits.enrollment.views.api.Client.access_token")
    mock_token = mocker.Mock()
    mock_token.access_token = "access_token"
    mock_token.expiry = time.time() + 10000
    mock_client.return_value = mock_token

    path = reverse(ROUTE_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    # mocked_access_token is a mocked version of the Client.access_token function
    # call it here to get the response, which has an access_token attribute
    assert data["token"] == mock_token.access_token


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_token_valid(mocker, client):
    mocker.patch("benefits.core.session.enrollment_token_valid", return_value=True)
    mocker.patch("benefits.core.session.enrollment_token", return_value="enrollment_token")

    path = reverse(ROUTE_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] == "enrollment_token"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_index_eligible(client):
    path = reverse(ROUTE_INDEX)
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.django_db
def test_index_ineligible(client):
    path = reverse(ROUTE_INDEX)
    with pytest.raises(AttributeError, match=r"eligibility"):
        client.get(path)
