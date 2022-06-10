from django.urls import reverse

import pytest


ROUTE_INDEX = "enrollment:index"


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
