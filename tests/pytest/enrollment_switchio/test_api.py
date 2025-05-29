from datetime import datetime
import pytest

from benefits.enrollment_switchio.api import Client


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
