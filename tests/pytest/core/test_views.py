import pytest
from django.urls import reverse
from benefits.core.models import TransitAgency

from tests.pytest.conftest import with_agency


@pytest.mark.django_db
def test_homepage_multiple_agencies(client):
    """Assumes that fixture data contains multiple active agencies."""
    path = reverse("core:index")
    response = client.get(path)
    assert response.status_code == 200
    assert "transit" in str(response.content)


@pytest.mark.django_db
def test_homepage_single_agency(mocker, client):
    agencies = TransitAgency.all_active()[:1]
    mocker.patch("benefits.core.models.TransitAgency.all_active", return_value=agencies)
    path = reverse("core:index")
    response = client.get(path)
    assert response.status_code == 302
    assert response.url == agencies[0].index_url


@pytest.mark.django_db
def test_help(client):
    path = reverse("core:help")
    response = client.get(path)
    assert response.status_code == 200
    assert "card" in str(response.content)


@pytest.mark.django_db
def test_help_with_agency(mocker, client):
    agency = TransitAgency.objects.first()
    assert agency
    with_agency(mocker, agency)

    path = reverse("core:help")
    response = client.get(path)
    assert response.status_code == 200
    assert agency.long_name in str(response.content)
