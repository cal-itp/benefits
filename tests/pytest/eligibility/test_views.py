from django.urls import reverse
import pytest
from typing import Tuple

from benefits.core import session
from benefits.core.models import TransitAgency, EligibilityVerifier
from benefits.eligibility.views import confirm
from tests.pytest.conftest import with_agency, initialize_request


def set_agency(mocker):
    agency = TransitAgency.objects.first()
    assert agency
    with_agency(mocker, agency)
    return agency


def set_verifier(mocker) -> Tuple[TransitAgency, EligibilityVerifier]:
    agency = set_agency(mocker)

    mock = mocker.patch("benefits.core.session.verifier", autospec=True)
    verifier = agency.eligibility_verifiers.first()
    assert verifier
    mock.return_value = verifier
    return (agency, verifier)


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


@pytest.mark.django_db
def test_confirm_success(mocker, rf):
    agency, verifier = set_verifier(mocker)

    path = reverse("eligibility:confirm")
    # currently, this corresponds to values from eligibility-server
    body = {"sub": "A1234567", "name": "Garcia"}
    request = rf.post(path, body)

    initialize_request(request)
    session.update(request, agency=agency, verifier=verifier, oauth_token="token")

    response = confirm(request)

    assert response.status_code == 302
    assert response.url == reverse("enrollment:index")
