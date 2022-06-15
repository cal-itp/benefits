import pytest

from benefits.eligibility.api import get_verified_types
from benefits.eligibility.forms import EligibilityVerificationForm


@pytest.fixture
def form(mocker):
    return mocker.Mock(spec=EligibilityVerificationForm, cleaned_data={"name": "Garcia", "sub": "A1234567"})


@pytest.fixture
def mock_api_client_verify(mocker):
    return mocker.patch("benefits.eligibility.api.Client.verify")


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_request_session")
def test_get_verified_types_error(mocker, app_request, mock_api_client_verify, form):
    api_errors = {"name": "Name error"}
    api_response = mocker.Mock(error=api_errors)
    mock_api_client_verify.return_value = api_response

    response = get_verified_types(app_request, form)

    assert response is None
    form.add_api_errors.assert_called_once_with(api_errors)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_request_session")
def test_get_verified_types_verified_types(mocker, app_request, mock_api_client_verify, form):
    verified_types = ["type1", "type2"]
    api_response = mocker.Mock(eligibility=verified_types, error=None)
    mock_api_client_verify.return_value = api_response

    response = get_verified_types(app_request, form)

    assert response == verified_types
    form.add_api_errors.assert_not_called()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_request_session")
def test_get_verified_types_no_verified_types(mocker, app_request, mock_api_client_verify, form):
    verified_types = []
    api_response = mocker.Mock(eligibility=verified_types, error=None)
    mock_api_client_verify.return_value = api_response

    response = get_verified_types(app_request, form)

    assert response == verified_types
    form.add_api_errors.assert_not_called()
