import pytest

from benefits.eligibility.forms import EligibilityVerificationForm


@pytest.fixture
def form(mocker):
    return mocker.Mock(spec=EligibilityVerificationForm, cleaned_data={"name": "Garcia", "sub": "A1234567"})


def mock_api_client_verify(mocker, response):
    return mocker.patch("benefits.eligibility.api.Client.verify", return_value=response)


def test_get_verified_types_error(mocker, app_request, form):
    pass


def test_get_verified_types_verified_types(mocker, app_request, form):
    pass


def test_get_verified_types_no_verified_types(mocker, app_request, form):
    pass
