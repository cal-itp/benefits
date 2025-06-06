from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib
import hmac
import json
from tempfile import NamedTemporaryFile
import requests


@dataclass
class Registration:
    regId: str
    gtwUrl: str


class EshopResponseMode(Enum):
    FRAGMENT = "fragment"
    QUERY = "query"
    FORM_POST = "form_post"
    POST_MESSAGE = "post_message"


@dataclass
class RegistrationStatus:
    regState: str
    created: datetime
    mode: str
    tokens: list[dict]
    eshopResponseMode: str
    identType: str = None
    maskCln: str = None
    cardExp: str = None


class Client:

    def __init__(
        self,
        api_url,
        api_key,
        api_secret,
        private_key,
        client_certificate,
        ca_certificate,
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.private_key = private_key
        self.client_certificate = client_certificate
        self.ca_certificate = ca_certificate

    def _signature_input_string(self, timestamp: str, method: str, request_path: str, body: str = None):
        if body is None:
            body = ""

        return f"{timestamp}{method}{request_path}{body}"

    def _stp_signature(self, timestamp: str, method: str, request_path, body: str = None):
        input_string = self._signature_input_string(timestamp, method, request_path, body)

        # must encode inputs for hashing, according to https://stackoverflow.com/a/66958131
        byte_key = self.api_secret.encode("utf-8")
        message = input_string.encode("utf-8")
        stp_signature = hmac.new(byte_key, message, hashlib.sha256).hexdigest()

        return stp_signature

    def _get_headers(self, method, request_path, request_body: dict = None):
        timestamp = str(int(datetime.now().timestamp()))

        return {
            "Content-Type": "application/json",
            "STP-APIKEY": self.api_key,
            "STP-TIMESTAMP": timestamp,
            "STP-SIGNATURE": self._stp_signature(
                timestamp=timestamp,
                method=method,
                request_path=request_path,
                body=json.dumps(request_body) if request_body else None,
            ),
        }

    def request_registration(
        self,
        eshopRedirectUrl: str,
        mode: str,
        eshopResponseMode: EshopResponseMode,
        timeout=5,
    ) -> Registration:
        registration_path = "/api/v1/registration"
        request_body = {
            "eshopRedirectUrl": eshopRedirectUrl,
            "mode": mode,
            "eshopResponseMode": eshopResponseMode.value,
        }

        response = self._cert_request(
            lambda verify, cert: requests.post(
                self.api_url.strip("/") + registration_path,
                json=request_body,
                headers=self._get_headers(method="POST", request_path=registration_path, request_body=request_body),
                cert=cert,
                verify=verify,
                timeout=timeout,
            )
        )

        response.raise_for_status()

        return Registration(**response.json())

    def get_registration_status(self, registration_id, timeout=5) -> RegistrationStatus:
        request_path = f"/api/v1/registration/{registration_id}"

        response = self._cert_request(
            lambda verify, cert: requests.get(
                self.api_url.strip("/") + request_path,
                headers=self._get_headers(method="GET", request_path=request_path),
                cert=cert,
                verify=verify,
                timeout=timeout,
            )
        )

        response.raise_for_status()

        return RegistrationStatus(**response.json())

    # see https://github.com/cal-itp/benefits/issues/2848 for more context about this
    def _cert_request(self, request_func):
        """
        Creates named (on-disk) temp files for client cert auth.
        * request_func: curried callable from `requests` library (e.g. `requests.get`).
        """
        # requests library reads temp files from file path
        # The "with" context destroys temp files when response comes back
        with NamedTemporaryFile("w+") as cert, NamedTemporaryFile("w+") as key, NamedTemporaryFile("w+") as ca:
            # write client cert data to temp files
            # resetting so they can be read again by requests
            cert.write(self.client_certificate)
            cert.seek(0)

            key.write(self.private_key)
            key.seek(0)

            ca.write(self.ca_certificate)
            ca.seek(0)

            # request using temp file paths
            return request_func(verify=ca.name, cert=(cert.name, key.name))
