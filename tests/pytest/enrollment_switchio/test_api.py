from datetime import datetime
import hashlib
import hmac
import json
import pytest

import benefits.enrollment_switchio.api
from benefits.enrollment_switchio.api import Client, EshopResponseMode, Registration


@pytest.fixture
def client():
    return Client("https://example.com", "api key", "api secret", None, None, None)


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("body", ['{"exampleProperty": "blah"}', None, ""])
def test_client_signature_input_string_with_body(client, method, body):
    timestamp = str(int(datetime.now().timestamp()))
    request_path = "/api/example"

    input_string = client._signature_input_string(timestamp=timestamp, method=method, request_path=request_path, body=body)

    if body is None:
        expected = f"{timestamp}{method}{request_path}"
    else:
        expected = f"{timestamp}{method}{request_path}{body}"

    assert input_string == expected


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("body", ['{"exampleProperty": "blah"}', None, ""])
def test_client_stp_signature(client, method, body):
    timestamp = str(int(datetime.now().timestamp()))
    request_path = "/api/example"

    stp_signature = client._stp_signature(timestamp=timestamp, method=method, request_path=request_path, body=body)

    # calculate the expected value
    byte_key = client.api_secret.encode("utf-8")
    input_string = client._signature_input_string(timestamp=timestamp, method=method, request_path=request_path, body=body)
    message = input_string.encode("utf-8")
    expected = hmac.new(byte_key, message, hashlib.sha256).hexdigest()

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
    mocker.patch("benefits.enrollment_switchio.api.requests.post", return_value=mock_response)

    registration = client.request_registration(
        eshopRedirectUrl="https://localhost/enrollment", mode="register", eshopResponseMode=EshopResponseMode.FORM_POST
    )

    assert registration == Registration(**mock_json)
