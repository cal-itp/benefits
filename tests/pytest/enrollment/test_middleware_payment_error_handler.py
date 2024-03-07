import pytest

from benefits.enrollment.middleware import HandleEnrollmentError, TEMPLATE_RETRY


@pytest.fixture
def mock_decorator_status_ok(mocker):
    mock_response = mocker.Mock(status_code=200, template_name="success.html")
    get_response = mocker.Mock(return_value=mock_response)
    return HandleEnrollmentError(get_response)


@pytest.fixture
def mock_decorator_status_error(mocker):
    get_response = mocker.Mock(side_effect=Exception("Enrollment error"))
    return HandleEnrollmentError(get_response)


@pytest.mark.django_db
def test_handle_enrollment_error_no_error(app_request, mock_decorator_status_ok):
    response = mock_decorator_status_ok(app_request)

    assert response.status_code == 200
    assert response.template_name == "success.html"


@pytest.mark.django_db
def test_handle_enrollment_error_error(app_request, mock_decorator_status_error):
    response = mock_decorator_status_error(app_request)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_RETRY
