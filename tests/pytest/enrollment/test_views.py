from django.urls import reverse
import pytest
from benefits.core.models import EligibilityType, TransitAgency

from tests.pytest.conftest import with_agency


def make_eligibile(mocker):
    agency = TransitAgency.objects.first()
    assert agency
    with_agency(mocker, agency)

    mock = mocker.patch("benefits.core.session.eligibility", autospec=True)
    eligibility = EligibilityType.objects.first()
    assert eligibility
    mock.return_value = eligibility


@pytest.mark.django_db
def test_index_eligible(mocker, client):
    make_eligibile(mocker)
    path = reverse("enrollment:index")
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.django_db
def test_index_ineligible(client):
    path = reverse("enrollment:index")
    with pytest.raises(AttributeError, match=r"eligibility"):
        client.get(path)
