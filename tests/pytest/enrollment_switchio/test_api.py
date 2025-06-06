from datetime import datetime
import json
import pytest

import benefits.enrollment_switchio.api
from benefits.enrollment_switchio.api import Client, EshopResponseMode, Registration, RegistrationStatus


@pytest.fixture
def client():
    return Client("https://example.com", "api key", "api secret", None, None, None)


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("body", ['{"exampleProperty": "blah"}', None, ""])
def test_client_signature_input_string(client, method, body):
    timestamp = str(int(datetime.now().timestamp()))
    request_path = "/api/example"

    input_string = client._signature_input_string(timestamp=timestamp, method=method, request_path=request_path, body=body)

    if body is None:
        expected = f"{timestamp}{method}{request_path}"
    else:
        expected = f"{timestamp}{method}{request_path}{body}"

    assert input_string == expected


def test_client_stp_signature(client):
    timestamp = "1748637999"
    method = "GET"
    request_path = "/api/example"
    body = '{"exampleProperty": "blah"}'

    stp_signature = client._stp_signature(timestamp=timestamp, method=method, request_path=request_path, body=body)

    # the expected STP-SIGNATURE value based on those inputs
    expected = "7da3dd8dad6af77d4f0d5b96ff250399f2ffe1dac2fdfbdbfae0c22a86366426"

    assert stp_signature == expected


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("body", [{"exampleProperty": "blah"}, None])
def test_get_headers(mocker, client, method, body):
    timestamp = 1516867520

    # mock datetime.now()
    datetime_mock = mocker.Mock()
    datetime_mock.now.return_value = datetime.fromtimestamp(timestamp)
    mocker.patch.object(benefits.enrollment_switchio.api, "datetime", datetime_mock)

    request_path = "/api/example"

    headers = client._get_headers(method=method, request_path=request_path, request_body=body)

    # calculate the expected value
    timestamp = str(timestamp)
    expected = {
        "Content-Type": "application/json",
        "STP-APIKEY": client.api_key,
        "STP-TIMESTAMP": timestamp,
        "STP-SIGNATURE": client._stp_signature(
            timestamp=timestamp,
            method=method,
            request_path=request_path,
            body=json.dumps(body) if body else None,
        ),
    }

    assert headers == expected


def test_client_request_registration(mocker, client):
    mock_response = mocker.Mock()
    mock_json = dict(regId="1234", gtwUrl="https://example.com/cst/?regId=1234")
    mock_response.json.return_value = mock_json
    mocker.patch("benefits.enrollment_switchio.api.Client._cert_request", return_value=mock_response)

    registration = client.request_registration(
        eshopRedirectUrl="https://localhost/enrollment", mode="register", eshopResponseMode=EshopResponseMode.FORM_POST
    )

    assert registration == Registration(**mock_json)


def test_client_get_registration_status(mocker, client):
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
    mocker.patch("benefits.enrollment_switchio.api.Client._cert_request", return_value=mock_response)

    registration_status = client.get_registration_status(registration_id="1234")

    assert registration_status == RegistrationStatus(**mock_json)
