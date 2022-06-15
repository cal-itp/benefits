import pytest

from benefits.eligibility.forms import EligibilityVerificationForm
from benefits.eligibility.verify import eligibility_from_api


@pytest.fixture
def form(mocker):
    return mocker.Mock(spec=EligibilityVerificationForm, cleaned_data={"name": "Garcia", "sub": "A1234567"})


@pytest.fixture
def mock_api_client_verify(mocker):
    return mocker.patch("benefits.eligibility.verify.Client.verify")


@pytest.mark.django_db
def test_eligibility_from_api_error(mocker, first_agency, first_verifier, mock_api_client_verify, form):
    api_errors = {"name": "Name error"}
    api_response = mocker.Mock(error=api_errors)
    mock_api_client_verify.return_value = api_response

    response = eligibility_from_api(first_verifier, form, first_agency)

    assert response is None
    form.add_api_errors.assert_called_once_with(api_errors)


@pytest.mark.django_db
def test_eligibility_from_api_verified_types(mocker, first_agency, first_verifier, mock_api_client_verify, form):
    verified_types = ["type1", "type2"]
    api_response = mocker.Mock(eligibility=verified_types, error=None)
    mock_api_client_verify.return_value = api_response

    response = eligibility_from_api(first_verifier, form, first_agency)

    assert response == verified_types
    form.add_api_errors.assert_not_called()


@pytest.mark.django_db
def test_eligibility_from_api_no_verified_types(mocker, first_agency, first_verifier, mock_api_client_verify, form):
    verified_types = []
    api_response = mocker.Mock(eligibility=verified_types, error=None)
    mock_api_client_verify.return_value = api_response

    response = eligibility_from_api(first_verifier, form, first_agency)

    assert response == verified_types
    form.add_api_errors.assert_not_called()
