from django.urls import reverse
import pytest
import httpretty
import requests

import datetime
import os
import uuid

from pathlib import Path
from jwcrypto import jwk, jwt
from typing import Tuple

from benefits.core import session
from benefits.core.models import TransitAgency, EligibilityVerifier
from benefits.eligibility.api import ApiError
from benefits.eligibility.views import confirm
from tests.pytest.conftest import with_agency, initialize_request


def set_agency(mocker):
    agency = TransitAgency.objects.first()
    assert agency
    with_agency(mocker, agency)
    return agency


def set_verifier(mocker) -> Tuple[TransitAgency, EligibilityVerifier]:
    agency = set_agency(mocker)

    mock = mocker.patch("benefits.core.session.verifier", autospec=True)
    verifier = agency.eligibility_verifiers.first()
    mocker.patch.object(verifier, "api_url", "http://localhost/verify")
    assert verifier
    mock.return_value = verifier
    return (agency, verifier)


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
        body=_make_token(
            {
                "jti": str(uuid.uuid4()),
                "iss": "test-server",
                "iat": int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()),
                "eligibility": ["type1"],
            },
            verifier.jws_signing_alg,
            _get_jwk("server.key"),
            verifier.jwe_encryption_alg,
            verifier.jwe_cek_enc,
            _get_jwk("client.pub"),
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


def _get_jwk(filename):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    file_path = current_path / "keys" / filename

    with file_path.open(mode="rb") as pemfile:
        key = jwk.JWK.from_pem(pemfile.read())

    return key


# copied and pasted from eligibility-server code for now - replace with eligibility-api function when available
def _make_token(payload, jws_signing_alg, server_private_key, jwe_encryption_alg, jwe_cek_enc, client_public_key):
    """Wrap payload in a signed and encrypted JWT for response."""
    # sign the payload with server's private key
    header = {"typ": "JWS", "alg": jws_signing_alg}
    signed_token = jwt.JWT(header=header, claims=payload)
    signed_token.make_signed_token(server_private_key)
    signed_payload = signed_token.serialize()
    # encrypt the signed payload with client's public key
    header = {"typ": "JWE", "alg": jwe_encryption_alg, "enc": jwe_cek_enc}
    encrypted_token = jwt.JWT(header=header, claims=signed_payload)
    encrypted_token.make_encrypted_token(client_public_key)
    return encrypted_token.serialize()


@httpretty.activate(verbose=True, allow_net_connect=False)
@pytest.mark.django_db
@pytest.mark.parametrize(
    "exception", [requests.ConnectionError, requests.Timeout, requests.TooManyRedirects, requests.HTTPError]
)
def test_confirm_failure_error_on_request(mocker, rf, exception):
    agency, verifier = set_verifier(mocker)

    # https://stackoverflow.com/questions/28675952/mock-a-http-request-that-times-out-with-httpretty
    def raise_exception(request, uri, headers):
        raise exception()

    httpretty.register_uri(httpretty.GET, "http://localhost/verify", status=200, body=raise_exception)

    path = reverse("eligibility:confirm")
    body = {"sub": "A7654321", "name": "Garcia"}
    request = rf.post(path, body)

    initialize_request(request)
    session.update(request, agency=agency, verifier=verifier, oauth_token="token")

    with pytest.raises(ApiError):
        confirm(request)
