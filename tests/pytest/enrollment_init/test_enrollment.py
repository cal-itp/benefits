import pytest
from requests import HTTPError

from benefits.enrollment.enrollment import Status
from benefits.enrollment_init.api import CardholderResponse, TransitAccountResponse
from benefits.enrollment_init.enrollment import enroll


@pytest.fixture
def mocked_TransitAccountResponse():
    return TransitAccountResponse(Id=1, CardholderId=100)


@pytest.fixture
def mocked_CardholderResponse_no_expiry(model_InitGroup):
    return CardholderResponse(FareCategory=model_InitGroup.group_id, FareCategoryExpiry=None)


@pytest.fixture
def card_token():
    return "card token"


@pytest.mark.django_db
@pytest.mark.parametrize("status_code", [500, 501, 502, 503, 504])
def test_enroll_system_error(
    mocker,
    status_code,
    app_request,
    model_InitConfig,
    model_EnrollmentFlow_does_not_support_expiration,
    model_InitGroup,
    card_token,
):
    mock_client_cls = mocker.patch("benefits.enrollment_init.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=status_code, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(response=mock_error_response)
    mock_client.post_cardholder.side_effect = http_error

    status, exception = enroll(
        request=app_request,
        init_config=model_InitConfig,
        flow=model_EnrollmentFlow_does_not_support_expiration,
        group=model_InitGroup,
        token=card_token,
    )

    assert status is Status.SYSTEM_ERROR
    assert exception == http_error


@pytest.mark.django_db
def test_enroll_exception_http_error_400(
    mocker,
    app_request,
    model_EnrollmentFlow_does_not_support_expiration,
    model_InitConfig,
    model_InitGroup,
    card_token,
):
    mock_client_cls = mocker.patch("benefits.enrollment_init.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=400, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(
        response=mock_error_response,
    )
    mock_client.post_cardholder.side_effect = http_error

    status, exception = enroll(
        request=app_request,
        init_config=model_InitConfig,
        flow=model_EnrollmentFlow_does_not_support_expiration,
        group=model_InitGroup,
        token=card_token,
    )

    assert status is Status.EXCEPTION
    assert isinstance(exception, Exception)
    assert exception.args[0] == f"{http_error}: {http_error.response.text}"


@pytest.mark.django_db
def test_enroll_exception_non_http_error(
    mocker,
    app_request,
    model_EnrollmentFlow_does_not_support_expiration,
    model_InitConfig,
    model_InitGroup,
    card_token,
):
    mock_client_cls = mocker.patch("benefits.enrollment_init.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_client.post_cardholder.side_effect = Exception("some other exception")

    status, exception = enroll(
        request=app_request,
        init_config=model_InitConfig,
        flow=model_EnrollmentFlow_does_not_support_expiration,
        group=model_InitGroup,
        token=card_token,
    )

    assert status is Status.EXCEPTION
    assert isinstance(exception, Exception)
    assert exception.args[0] == "some other exception"


@pytest.mark.django_db
@pytest.mark.usefixtures("model_InitGroup")
def test_enroll_success_flow_does_not_support_expiration_no_expiry(
    mocker,
    app_request,
    model_EnrollmentFlow_does_not_support_expiration,
    model_InitConfig,
    model_InitGroup,
    card_token,
    mocked_TransitAccountResponse,
):
    mock_client_cls = mocker.patch("benefits.enrollment_init.enrollment.Client")
    mock_client = mock_client_cls.return_value

    mock_client.get_transit_account.return_value = mocked_TransitAccountResponse

    status, exception = enroll(
        request=app_request,
        init_config=model_InitConfig,
        flow=model_EnrollmentFlow_does_not_support_expiration,
        group=model_InitGroup,
        token=card_token,
    )

    mock_client.post_cardholder.assert_called_once_with(
        fare_category=model_InitGroup.group_id,
        transit_account_id=mocked_TransitAccountResponse.Id,
    )
    assert status is Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
def test_enroll_success_flow_does_not_support_expiration_customer_already_enrolled_no_expiry(
    mocker,
    app_request,
    model_EnrollmentFlow_does_not_support_expiration,
    model_InitConfig,
    model_InitGroup,
    card_token,
    mocked_TransitAccountResponse,
    mocked_CardholderResponse_no_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment_init.enrollment.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_transit_account.return_value = mocked_TransitAccountResponse
    mock_client.get_cardholder.return_value = mocked_CardholderResponse_no_expiry

    status, exception = enroll(
        request=app_request,
        init_config=model_InitConfig,
        flow=model_EnrollmentFlow_does_not_support_expiration,
        group=model_InitGroup,
        token=card_token,
    )

    mock_client.post_cardholder.assert_not_called()

    assert status is Status.SUCCESS
    assert exception is None
