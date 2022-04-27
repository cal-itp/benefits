from django.urls import reverse
import pytest

from benefits.core.models import TransitAgency
from tests.pytest.conftest import with_agency


def set_agency(mocker):
    agency = TransitAgency.objects.first()
    assert agency
    with_agency(mocker, agency)
    return agency


def set_verifier(mocker):
    agency = set_agency(mocker)

    mock = mocker.patch("benefits.core.session.verifier", autospec=True)
    verifier = agency.eligibility_verifiers.first()
    assert verifier
    mock.return_value = verifier


@pytest.mark.django_db
def test_index_with_agency(mocker, client):
    set_agency(mocker)
    path = reverse("eligibility:index")
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.django_db
def test_index_without_agency(mocker, client):
    with_agency(mocker, None)

    path = reverse("eligibility:index")
    with pytest.raises(AttributeError, match=r"agency"):
        client.get(path)


@pytest.mark.django_db
def test_start_with_verifier(mocker, client):
    set_verifier(mocker)
    path = reverse("eligibility:start")
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.django_db
def test_start_without_verifier(mocker, client):
    set_agency(mocker)
    path = reverse("eligibility:start")
    with pytest.raises(AttributeError, match=r"verifier"):
        client.get(path)
