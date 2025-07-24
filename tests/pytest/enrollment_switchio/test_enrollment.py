from django.conf import settings
import pytest
from requests import HTTPError
from benefits.enrollment.enrollment import Status
from benefits.enrollment_switchio.api import EshopResponseMode, GroupExpiry, Registration, RegistrationMode, RegistrationStatus
from benefits.enrollment_switchio.enrollment import (
    enroll,
    get_registration_status,
    request_registration,
    get_latest_active_token_value,
)


@pytest.fixture
def mocked_registration():
    return Registration(regId="1111", gtwUrl="https://example.com/?regId=1111")


@pytest.fixture
def mocked_registration_status():
    return RegistrationStatus(
        regState="created",
        created="2025-06-11T00:00:00",
        mode=RegistrationMode.REGISTER.value,
        tokens=[],
        eshopResponseMode=EshopResponseMode.FORM_POST.value,
    )


@pytest.fixture
def mocked_api_base_url(mocker):
    return mocker.patch(
        "benefits.enrollment_switchio.models.get_secret_by_name", return_value="https://example.com/backend-api"
    )


@pytest.fixture
def card_token():
    return "card token"


@pytest.fixture
def mocked_group_expiry_no_expiry():
    return GroupExpiry(group="senior-discount", expiresAt=None)


@pytest.fixture
def mocked_group_expiry_with_expiry():
    return GroupExpiry(group="senior-discount", expiresAt="2025-01-01T00:00:00")


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url")
def test_request_registration_success(mocker, app_request, model_SwitchioConfig, mocked_registration):
    mocker.patch(
        "benefits.enrollment_switchio.enrollment.TokenizationClient.request_registration", return_value=mocked_registration
    )

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

    mocker.patch("benefits.enrollment_switchio.enrollment.TokenizationClient.request_registration", side_effect=http_error)

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

    mocker.patch("benefits.enrollment_switchio.enrollment.TokenizationClient.request_registration", side_effect=http_error)

    registration_response = request_registration(app_request, model_SwitchioConfig)

    assert registration_response.status == Status.EXCEPTION
    assert registration_response.exception == http_error
    assert isinstance(registration_response.exception, HTTPError)
    assert registration_response.registration is None


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url")
def test_request_registration_non_http_error(mocker, app_request, model_SwitchioConfig):

    mocker.patch(
        "benefits.enrollment_switchio.enrollment.TokenizationClient.request_registration",
        side_effect=Exception("some other exception"),
    )

    registration_response = request_registration(app_request, model_SwitchioConfig)

    assert registration_response.status == Status.EXCEPTION
    assert isinstance(registration_response.exception, Exception)
    assert registration_response.registration is None


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url")
def test_get_registration_status_success(mocker, model_SwitchioConfig, mocked_registration_status):
    mocker.patch(
        "benefits.enrollment_switchio.enrollment.TokenizationClient.get_registration_status",
        return_value=mocked_registration_status,
    )

    response = get_registration_status(model_SwitchioConfig, registration_id="1234")

    assert response.status == Status.SUCCESS
    assert response.registration_status == mocked_registration_status


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url")
@pytest.mark.parametrize("status_code", [500, 501, 502, 503, 504])
def test_get_registration_status_system_error(mocker, status_code, model_SwitchioConfig):
    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=status_code, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(response=mock_error_response)

    mocker.patch("benefits.enrollment_switchio.enrollment.TokenizationClient.get_registration_status", side_effect=http_error)

    response = get_registration_status(switchio_config=model_SwitchioConfig, registration_id="4321")

    assert response.status == Status.SYSTEM_ERROR
    assert response.exception == http_error
    assert response.registration_status is None


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url")
def test_get_registration_status_http_error_400(mocker, app_request, model_SwitchioConfig):
    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=400, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(response=mock_error_response)

    mocker.patch("benefits.enrollment_switchio.enrollment.TokenizationClient.get_registration_status", side_effect=http_error)

    response = get_registration_status(switchio_config=model_SwitchioConfig, registration_id="4321")

    assert response.status == Status.EXCEPTION
    assert response.exception == http_error
    assert isinstance(response.exception, HTTPError)
    assert response.registration_status is None


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url")
def test_get_registration_status_non_http_error(mocker, model_SwitchioConfig):

    mocker.patch(
        "benefits.enrollment_switchio.enrollment.TokenizationClient.get_registration_status",
        side_effect=Exception("some other exception"),
    )

    response = get_registration_status(switchio_config=model_SwitchioConfig, registration_id="1234")

    assert response.status == Status.EXCEPTION
    assert isinstance(response.exception, Exception)
    assert response.registration_status is None


@pytest.mark.parametrize(
    "tokens,expected_token_value",
    [
        (
            [
                {
                    "token": "abcd",
                    "par": None,
                    "tokenVersion": 100,
                    "tokenState": "active",
                    "validFrom": "2025-01-11T10:46:00.000",
                    "validTo": "2050-01-11T10:46:00.000",
                    "testOnly": False,
                },
            ],
            "abcd",
        ),
        (
            [
                {
                    "token": "abcd",
                    "par": None,
                    "tokenVersion": 100,
                    "tokenState": "active",
                    "validFrom": "2025-01-11T10:46:00.000",
                    "validTo": "2050-01-11T10:46:00.000",
                    "testOnly": False,
                },
                {
                    "token": "1357",
                    "par": None,
                    "tokenVersion": 100,
                    "tokenState": "active",
                    "validFrom": "2025-01-12T10:46:00.000",
                    "validTo": "2050-01-12T10:46:00.000",
                    "testOnly": False,
                },
            ],
            "1357",
        ),
        (
            [
                {
                    "token": "abcd",
                    "par": None,
                    "tokenVersion": 100,
                    "tokenState": "active",
                    "validFrom": "2025-01-11T10:46:00.000",
                    "validTo": "2050-01-11T10:46:00.000",
                    "testOnly": False,
                },
                {
                    "token": "1357",
                    "par": None,
                    "tokenVersion": 100,
                    "tokenState": "invalid",
                    "validFrom": "2025-01-12T10:46:00.000",
                    "validTo": "2050-01-12T10:46:00.000",
                    "testOnly": False,
                },
            ],
            "abcd",
        ),
    ],
)
def test_get_latest_active_token_value(mocker, tokens, expected_token_value):
    token_value = get_latest_active_token_value(tokens)

    assert token_value == expected_token_value


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url", "model_SwitchioGroup")
@pytest.mark.parametrize("status_code", [500, 501, 502, 503, 504])
def test_enroll_system_error(
    mocker,
    status_code,
    model_SwitchioConfig,
    model_EnrollmentFlow_does_not_support_expiration,
    card_token,
):
    mock_client_cls = mocker.patch("benefits.enrollment_switchio.enrollment.EnrollmentClient")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=status_code, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(response=mock_error_response)
    mock_client.add_group_to_token.side_effect = http_error

    status, exception = enroll(
        switchio_config=model_SwitchioConfig,
        flow=model_EnrollmentFlow_does_not_support_expiration,
        token=card_token,
    )

    assert status is Status.SYSTEM_ERROR
    assert exception == http_error


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url", "model_SwitchioGroup")
def test_enroll_exception_http_error_400(
    mocker,
    model_EnrollmentFlow_does_not_support_expiration,
    model_SwitchioConfig,
    card_token,
):
    mock_client_cls = mocker.patch("benefits.enrollment_switchio.enrollment.EnrollmentClient")
    mock_client = mock_client_cls.return_value

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=400, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(
        response=mock_error_response,
    )
    mock_client.add_group_to_token.side_effect = http_error

    status, exception = enroll(
        switchio_config=model_SwitchioConfig,
        flow=model_EnrollmentFlow_does_not_support_expiration,
        token=card_token,
    )

    assert status is Status.EXCEPTION
    assert isinstance(exception, Exception)
    assert exception.args[0] == f"{http_error}: {http_error.response.json()}"


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_api_base_url",
    "model_SwitchioGroup",
)
def test_enroll_exception_non_http_error(
    mocker,
    model_EnrollmentFlow_does_not_support_expiration,
    model_SwitchioConfig,
    card_token,
):
    mock_client_cls = mocker.patch("benefits.enrollment_switchio.enrollment.EnrollmentClient")
    mock_client = mock_client_cls.return_value

    mock_client.add_group_to_token.side_effect = Exception("some other exception")

    status, exception = enroll(
        switchio_config=model_SwitchioConfig,
        flow=model_EnrollmentFlow_does_not_support_expiration,
        token=card_token,
    )

    assert status is Status.EXCEPTION
    assert isinstance(exception, Exception)
    assert exception.args[0] == "some other exception"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url", "model_SwitchioGroup")
def test_enroll_success_flow_does_not_support_expiration_customer_already_enrolled_no_expiry(
    mocker, model_EnrollmentFlow_does_not_support_expiration, model_SwitchioConfig, card_token, mocked_group_expiry_no_expiry
):
    mock_client_cls = mocker.patch("benefits.enrollment_switchio.enrollment.EnrollmentClient")
    mock_client = mock_client_cls.return_value
    mock_client.get_groups_for_token.return_value = [mocked_group_expiry_no_expiry]

    status, exception = enroll(
        switchio_config=model_SwitchioConfig,
        flow=model_EnrollmentFlow_does_not_support_expiration,
        token=card_token,
    )

    mock_client.add_group_to_token.assert_not_called()

    assert status is Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url", "model_SwitchioGroup")
def test_enroll_success_flow_does_not_support_expiration_no_expiry(
    mocker,
    model_EnrollmentFlow_does_not_support_expiration,
    model_SwitchioConfig,
    card_token,
):
    mock_client_cls = mocker.patch("benefits.enrollment_switchio.enrollment.EnrollmentClient")
    mock_client = mock_client_cls.return_value

    status, exception = enroll(
        switchio_config=model_SwitchioConfig,
        flow=model_EnrollmentFlow_does_not_support_expiration,
        token=card_token,
    )

    mock_client.add_group_to_token.assert_called_once_with(
        pto_id=model_SwitchioConfig.pto_id,
        group_id=model_EnrollmentFlow_does_not_support_expiration.group_id,
        token=card_token,
        timeout=settings.REQUESTS_TIMEOUT,
    )
    assert status is Status.SUCCESS
    assert exception is None


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_api_base_url", "model_SwitchioGroup")
def test_enroll_does_not_support_expiration_has_expiration_date(
    mocker,
    model_EnrollmentFlow_does_not_support_expiration,
    model_SwitchioConfig,
    card_token,
    mocked_group_expiry_with_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment_switchio.enrollment.EnrollmentClient")
    mock_client = mock_client_cls.return_value

    # mock that a funding source already exists, doesn't matter what expiry_date is
    mocker.patch(
        "benefits.enrollment_switchio.enrollment._get_group_for_token",
        return_value=mocked_group_expiry_with_expiry,
    )

    status, exception = enroll(
        switchio_config=model_SwitchioConfig,
        flow=model_EnrollmentFlow_does_not_support_expiration,
        token=card_token,
    )

    assert status is Status.SUCCESS
    mock_client.add_group_to_token.assert_called_once_with(
        pto_id=model_SwitchioConfig.pto_id,
        group_id=model_EnrollmentFlow_does_not_support_expiration.group_id,
        token=card_token,
        timeout=settings.REQUESTS_TIMEOUT,
    )
