import pytest

from benefits.eligibility.api import get_verified_types
from benefits.eligibility.forms import EligibilityVerificationForm

from tests.pytest.conftest import set_verifier


@pytest.fixture
def form(mocker):
    return mocker.Mock(spec=EligibilityVerificationForm, cleaned_data={"name": "Garcia", "sub": "A1234567"})


def mock_api_client_verify(mocker, response):
    return mocker.patch("benefits.eligibility.api.Client.verify", return_value=response)


@pytest.mark.django_db
def test_get_verified_types_error(mocker, app_request, form):
    set_verifier(mocker)

    api_errors = {"name": "Name error"}
    api_response = mocker.Mock(error=api_errors)

    mock_api_client_verify(mocker, api_response)

    response = get_verified_types(app_request, form)

    assert response is None
    form.add_api_errors.assert_called_once_with(api_errors)


def test_get_verified_types_verified_types(mocker, app_request, form):
    pass


def test_get_verified_types_no_verified_types(mocker, app_request, form):
    pass
