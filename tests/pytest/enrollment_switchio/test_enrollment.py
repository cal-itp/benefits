import pytest
from requests import HTTPError
from benefits.enrollment.enrollment import Status
from benefits.enrollment_switchio.api import Registration
from benefits.enrollment_switchio.enrollment import request_registration


@pytest.fixture
def mocked_registration():
    return Registration(regId="1111", gtwUrl="https://example.com/?regId=1111")


@pytest.fixture
def mocked_api_base_url(mocker):
    return mocker.patch(
        "benefits.enrollment_switchio.models.get_secret_by_name", return_value="https://example.com/backend-api"
    )


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url")
def test_request_registration_success(mocker, app_request, model_SwitchioConfig, mocked_registration):
    mocker.patch("benefits.enrollment_switchio.enrollment.Client.request_registration", return_value=mocked_registration)

    registration_response = request_registration(app_request, model_SwitchioConfig)

    assert registration_response.status == Status.SUCCESS
    assert registration_response.registration == mocked_registration


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url")
@pytest.mark.parametrize("status_code", [500, 501, 502, 503, 504])
def test_request_registration_system_error(mocker, status_code, app_request, model_SwitchioConfig):
    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=status_code, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(response=mock_error_response)

    mocker.patch("benefits.enrollment_switchio.enrollment.Client.request_registration", side_effect=http_error)

    registration_response = request_registration(app_request, model_SwitchioConfig)

    assert registration_response.status == Status.SYSTEM_ERROR
    assert registration_response.exception == http_error
    assert registration_response.registration is None


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url")
def test_request_registration_http_error_400(mocker, app_request, model_SwitchioConfig):
    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=400, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(response=mock_error_response)

    mocker.patch("benefits.enrollment_switchio.enrollment.Client.request_registration", side_effect=http_error)

    registration_response = request_registration(app_request, model_SwitchioConfig)

    assert registration_response.status == Status.EXCEPTION
    assert registration_response.exception == http_error
    assert isinstance(registration_response.exception, HTTPError)
    assert registration_response.registration is None


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url")
def test_request_registration_non_http_error(mocker, app_request, model_SwitchioConfig):

    mocker.patch(
        "benefits.enrollment_switchio.enrollment.Client.request_registration", side_effect=Exception("some other exception")
    )

    registration_response = request_registration(app_request, model_SwitchioConfig)

    assert registration_response.status == Status.EXCEPTION
    assert isinstance(registration_response.exception, Exception)
    assert registration_response.registration is None
