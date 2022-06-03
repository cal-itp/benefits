import datetime
import os
import uuid
from pathlib import Path

from django.urls import reverse

import pytest
import httpretty
import requests

from benefits.core import session
from eligibility_api.client import ApiError, TokenError
from eligibility_api.server import make_token
from benefits.eligibility.views import confirm
from tests.pytest.conftest import initialize_request, set_agency, set_verifier, with_agency


@pytest.mark.django_db
def test_index_with_agency(mocker, client):
    set_agency(mocker)
    path = reverse("eligibility:index")
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.django_db
def test_index_without_agency(mocker, client):
    with_agency(mocker, None)

    path = reverse("eligibility:index")
    with pytest.raises(AttributeError, match=r"agency"):
        client.get(path)


@pytest.mark.django_db
def test_start_with_verifier(mocker, client):
    set_verifier(mocker)
    path = reverse("eligibility:start")
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.django_db
def test_start_without_verifier(mocker, client):
    set_agency(mocker)
    path = reverse("eligibility:start")
    with pytest.raises(AttributeError, match=r"verifier"):
        client.get(path)


@httpretty.activate(verbose=True, allow_net_connect=False)
@pytest.mark.django_db
def test_confirm_success(mocker, rf):
    agency, verifier = set_verifier(mocker)

    # Mock the eligibility-server response using HTTPretty
    # https://stackoverflow.com/questions/21877387/mocking-a-http-server-in-python
    httpretty.register_uri(
        httpretty.GET,
        "http://localhost/verify",
        status=200,
        body=make_token(
            {
                "jti": str(uuid.uuid4()),
                "iss": "test-server",
                "iat": int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()),
                "eligibility": ["type1"],
            },
            verifier.jws_signing_alg,
            _get_key("server.key"),
            verifier.jwe_encryption_alg,
            verifier.jwe_cek_enc,
            _get_key("client.pub"),
        ),
    )

    path = reverse("eligibility:confirm")
    body = {"sub": "A0101011", "name": "Lastname"}
    request = rf.post(path, body)

    initialize_request(request)
    session.update(request, agency=agency, verifier=verifier, oauth_token="token")

    response = confirm(request)

    assert response.status_code == 302
    assert response.url == reverse("enrollment:index")


def _get_key(filename):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    file_path = current_path / "keys" / filename

    with file_path.open(mode="rb") as pemfile:
        key = str(pemfile.read(), "utf-8")

    return key


@httpretty.activate(verbose=True, allow_net_connect=False)
@pytest.mark.django_db
@pytest.mark.parametrize(
    "exception", [requests.ConnectionError, requests.Timeout, requests.TooManyRedirects, requests.HTTPError]
)
def test_confirm_failure_error_on_request(mocker, rf, exception):
    agency, verifier = set_verifier(mocker)

    def raise_exception(*args, **kwargs):
        raise exception()

    mocker.patch("requests.get", new=raise_exception)

    path = reverse("eligibility:confirm")
    body = {"sub": "A7654321", "name": "Garcia"}
    request = rf.post(path, body)

    initialize_request(request)
    session.update(request, agency=agency, verifier=verifier, oauth_token="token")

    with pytest.raises(ApiError):
        confirm(request)


@httpretty.activate(verbose=True, allow_net_connect=False)
@pytest.mark.django_db
def test_confirm_failure_unexpected_status_code(mocker, rf):
    agency, verifier = set_verifier(mocker)

    httpretty.register_uri(httpretty.GET, "http://localhost/verify", status=404)

    path = reverse("eligibility:confirm")
    body = {"sub": "A1234567", "name": "Garcia"}
    request = rf.post(path, body)

    initialize_request(request)
    session.update(request, agency=agency, verifier=verifier, oauth_token="token")

    with pytest.raises(ApiError, match=r"Unexpected eligibility"):
        confirm(request)


@httpretty.activate(verbose=True, allow_net_connect=False)
@pytest.mark.django_db
def test_confirm_failure_error_tokenizing_request(mocker, rf):
    agency, verifier = set_verifier(mocker)
    agency.jws_signing_alg = "not real"

    path = reverse("eligibility:confirm")
    body = {"sub": "A0101011", "name": "Lastname"}
    request = rf.post(path, body)

    initialize_request(request)
    session.update(request, agency=agency, verifier=verifier, oauth_token="token")

    with pytest.raises(TokenError):
        confirm(request)


def _tokenize_response_error_scenarios():
    return [
        pytest.param(lambda verifier: "", id='TokenError("Invalid response format")'),
        pytest.param(lambda verifier: "invalid token", id='TokenError("Invalid JWE token")'),
        pytest.param(
            lambda verifier: make_token(
                {
                    "jti": str(uuid.uuid4()),
                    "iss": "test-server",
                    "iat": int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()),
                    "eligibility": ["type1"],
                },
                "RS512",  # signing algorithm that doesn't match verifier.jws_signing_alg
                _get_key("server.key"),
                verifier.jwe_encryption_alg,
                verifier.jwe_cek_enc,
                _get_key("client.pub"),
            ),
            id='TokenError("JWS token signature verification failed")',
        ),
    ]


@httpretty.activate(verbose=True, allow_net_connect=False)
@pytest.mark.django_db
@pytest.mark.parametrize("body_lambda", _tokenize_response_error_scenarios())
def test_confirm_failure_error_tokenizing_response(mocker, rf, body_lambda):
    agency, verifier = set_verifier(mocker)

    httpretty.register_uri(
        httpretty.GET,
        "http://localhost/verify",
        status=200,
        body=body_lambda(verifier),
    )

    path = reverse("eligibility:confirm")
    body = {"sub": "A1234567", "name": "Garcia"}
    request = rf.post(path, body)

    initialize_request(request)
    session.update(request, agency=agency, verifier=None, oauth_token="token")

    with pytest.raises(TokenError):
        confirm(request)
