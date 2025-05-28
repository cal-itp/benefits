from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib
import hmac
import json
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
    identifier_type: str = None
    mask_cin: str = None
    card_exp: str = None


class Client:

    def __init__(
        self,
        api_url,
        api_key,
        api_secret,
        private_key,
        client_certificate_file,
        ca_certificate,
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.private_key = private_key
        self.client_certificate_file = client_certificate_file
        self.ca_certificate = ca_certificate

    def _signature_input_string(self, timestamp, method, request_path, body=None):
        if body is None:
            body = ""

        return f"{timestamp}{method}{request_path}{body}"

    def _stp_signature(self, api_secret, timestamp, method, request_path, body=None):
        input_string = self._signature_input_string(timestamp, method, request_path, body)

        # must encode inputs for hashing, according to https://stackoverflow.com/a/66958131
        byte_key = api_secret.encode("utf-8")
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
                api_secret=self.api_secret,
                timestamp=timestamp,
                method=method,
                request_path=request_path,
                body=json.dumps(request_body) if request_body else None,
            ),
        }

    def request_registration(
        self,
        eshopResponseMode: EshopResponseMode,
        timeout=5,
    ) -> Registration:
        registration_path = "/api/v1/registration"
        request_body = {
            "eshopRedirectUrl": "http://localhost:11369/enrollment",
            "mode": "register",
            "eshopResponseMode": eshopResponseMode.value,
        }
        cert = (self.client_certificate_file, self.private_key)

        response = requests.post(
            self.api_url.strip("/") + registration_path,
            json=request_body,
            headers=self._get_headers(method="POST", request_path=registration_path, request_body=request_body),
            cert=cert,
            verify=self.ca_certificate,
            timeout=timeout,
        )

        response.raise_for_status()

        return Registration(**response.json())

    def get_registration_status(self, registration_id, timeout=5) -> RegistrationStatus:
        request_path = f"/api/v1/registration/{registration_id}"
        cert = (self.client_certificate_file, self.private_key)

        response = requests.get(
            self.api_url.strip("/") + request_path,
            headers=self._get_headers(method="GET", request_path=request_path),
            cert=cert,
            verify=self.ca_certificate,
            timeout=timeout,
        )

        response.raise_for_status()

        return RegistrationStatus(**response.json())
