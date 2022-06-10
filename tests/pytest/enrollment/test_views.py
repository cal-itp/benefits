from django.urls import reverse

import pytest


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligibility")
def test_index_eligible(client):
    path = reverse("enrollment:index")
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.django_db
def test_index_ineligible(client):
    path = reverse("enrollment:index")
    with pytest.raises(AttributeError, match=r"eligibility"):
        client.get(path)
