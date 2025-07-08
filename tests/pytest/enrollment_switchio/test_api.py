from datetime import datetime
import json
import pytest

import benefits.enrollment_switchio.api
from benefits.enrollment_switchio.api import (
    EnrollmentClient,
    Group,
    TokenizationClient,
    EshopResponseMode,
    Registration,
    RegistrationMode,
    RegistrationStatus,
)


@pytest.fixture
def tokenization_client():
    return TokenizationClient("https://example.com", "api key", "api secret", None, None, None)


@pytest.fixture
def enrollment_client():
    return EnrollmentClient("https://example.com", "Basic abc123", None, None, None)


@pytest.mark.django_db
def test_tokenization_client_cert_request(mocker, tokenization_client):
    temp_file = mocker.patch("benefits.enrollment_switchio.api.NamedTemporaryFile")
    request_func = mocker.Mock()

    tokenization_client._cert_request(request_func)

    temp_file.assert_called()
    request_func.assert_called_once()
    assert "verify" in request_func.call_args.kwargs
    assert "cert" in request_func.call_args.kwargs


@pytest.mark.django_db
def test_enrollment_client_cert_request(mocker, enrollment_client):
    temp_file = mocker.patch("benefits.enrollment_switchio.api.NamedTemporaryFile")
    request_func = mocker.Mock()

    enrollment_client._cert_request(request_func)

    temp_file.assert_called()
    request_func.assert_called_once()
    assert "verify" in request_func.call_args.kwargs
    assert "cert" in request_func.call_args.kwargs


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("body", ['{"exampleProperty": "blah"}', None, ""])
def test_tokenization_client_signature_input_string(tokenization_client, method, body):
    timestamp = str(int(datetime.now().timestamp()))
    request_path = "/api/example"

    input_string = tokenization_client._signature_input_string(
        timestamp=timestamp, method=method, request_path=request_path, body=body
    )

    if body is None:
        expected = f"{timestamp}{method}{request_path}"
    else:
        expected = f"{timestamp}{method}{request_path}{body}"

    assert input_string == expected


def test_tokenization_client_stp_signature(tokenization_client):
    timestamp = "1748637999"
    method = "GET"
    request_path = "/api/example"
    body = '{"exampleProperty": "blah"}'

    stp_signature = tokenization_client._stp_signature(
        timestamp=timestamp, method=method, request_path=request_path, body=body
    )

    # the expected STP-SIGNATURE value based on those inputs
    expected = "7da3dd8dad6af77d4f0d5b96ff250399f2ffe1dac2fdfbdbfae0c22a86366426"

    assert stp_signature == expected


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("body", [{"exampleProperty": "blah"}, None])
def test_tokenization_client_get_headers(mocker, tokenization_client, method, body):
    timestamp = 1516867520

    # mock datetime.now()
    datetime_mock = mocker.Mock()
    datetime_mock.now.return_value = datetime.fromtimestamp(timestamp)
    mocker.patch.object(benefits.enrollment_switchio.api, "datetime", datetime_mock)

    request_path = "/api/example"

    headers = tokenization_client._get_headers(method=method, request_path=request_path, request_body=body)

    # calculate the expected value
    timestamp = str(timestamp)
    expected = {
        "STP-APIKEY": tokenization_client.api_key,
        "STP-TIMESTAMP": timestamp,
        "STP-SIGNATURE": tokenization_client._stp_signature(
            timestamp=timestamp,
            method=method,
            request_path=request_path,
            body=json.dumps(body) if body else None,
        ),
    }

    assert headers == expected


def test_tokenization_client_request_registration(mocker, tokenization_client):
    mock_response = mocker.Mock()
    mock_json = dict(regId="1234", gtwUrl="https://example.com/cst/?regId=1234")
    mock_response.json.return_value = mock_json
    mocker.patch("benefits.enrollment_switchio.api.TokenizationClient._cert_request", return_value=mock_response)

    registration = tokenization_client.request_registration(
        eshopRedirectUrl="https://localhost/enrollment",
        mode=RegistrationMode.REGISTER,
        eshopResponseMode=EshopResponseMode.FORM_POST,
    )

    assert registration == Registration(**mock_json)


def test_tokenization_client_get_registration_status(mocker, tokenization_client):
    mock_response = mocker.Mock()
    mock_json = dict(
        regState="created",
        created="2025-05-28T18:26:03.353",
        mode="register",
        tokens=[],
        eshopResponseMode="form_post",
        identType="BPK",
        maskCln="412501****1234",
        cardExp="1119",
    )
    mock_response.json.return_value = mock_json
    mocker.patch("benefits.enrollment_switchio.api.TokenizationClient._cert_request", return_value=mock_response)

    registration_status = tokenization_client.get_registration_status(registration_id="1234")

    assert registration_status == RegistrationStatus(**mock_json)


def test_enrollment_client_healthcheck(mocker, enrollment_client):
    mock_response = mocker.Mock()
    mock_response.text.return_value = "Egibility is alive!"
    mocker.patch("benefits.enrollment_switchio.api.EnrollmentClient._cert_request", return_value=mock_response)

    response = enrollment_client.healthcheck()

    assert response == mock_response.text


def test_enrollment_client_get_groups(mocker, enrollment_client):
    mock_response = mocker.Mock()
    mock_json = dict(
        id=1,
        operatorId=123,
        name="Veteran Discount",
        code="veteran-discount",
        value=10,
    )
    mock_response.json.return_value = [mock_json]
    mocker.patch("benefits.enrollment_switchio.api.EnrollmentClient._cert_request", return_value=mock_response)

    groups = enrollment_client.get_groups(pto_id="123")

    assert groups == [Group(**mock_json)]


def test_enrollment_client_get_groups_for_token(mocker, enrollment_client):
    mock_response = mocker.Mock()
    mock_json = dict(group="veteran-discount", expiresAt=None)
    mock_response.json.return_value = [mock_json]
    mocker.patch("benefits.enrollment_switchio.api.EnrollmentClient._cert_request", return_value=mock_response)

    groups = enrollment_client.get_groups_for_token(pto_id="123", token="abcde12345")

    assert groups == [mock_json]


def test_enrollment_client_add_group_to_token(mocker, enrollment_client):
    mock_response = mocker.Mock()
    mock_response.text.return_value = "Groups added or updated successfully"
    mocker.patch("benefits.enrollment_switchio.api.EnrollmentClient._cert_request", return_value=mock_response)

    response = enrollment_client.add_group_to_token("123", "veteran-discount", "abcde12345")

    assert response == mock_response.text


def test_enrollment_client_remove_group_from_token(mocker, enrollment_client):
    group_code = "veteran-discount"
    token = "abcde12345"

    mock_response = mocker.Mock()
    mock_response.text.return_value = f"Discount {group_code} removed successfully for token {token}"
    mocker.patch("benefits.enrollment_switchio.api.EnrollmentClient._cert_request", return_value=mock_response)

    response = enrollment_client.remove_group_from_token("123", group_code, token)

    assert response == mock_response.text
