"""
The eligibility application: Eligibility Verification API implementation.
"""
import base64
import datetime
import json
import uuid

import requests

from eligibility_verification.settings import ALLOWED_HOSTS


class Response():
    """Eligibility Verification API response."""

    def __init__(self, token):
        token_bytes = bytes(token, "utf-8")
        dec = str(base64.urlsafe_b64decode(token_bytes), "utf-8")
        payload = json.loads(dec)

        self._payload = dict(
            jti=str(payload.get("jti")),
            iss=str(payload.get("iss")),
            iat=int(payload.get("iat")),
            eligibility=list(payload.get("eligibility", [])),
            error=json.loads(payload.get("error", "{}"))
        )

    def __repr__(self):
        return str(self)

    def __str__(self):
        return json.dumps(self._payload)

    def verified(self):
        return len(self._payload["eligibility"]) > 0


class Token():
    """Eligibility Verification API request token."""

    def __init__(self, **kwargs):
        self._payload = dict(
            jti=str(uuid.uuid4()),
            iss=ALLOWED_HOSTS[0],
            iat=int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()),
            agency=kwargs.get("agency"),
            eligibility=kwargs.get("eligibility"),
            sub=kwargs.get("sub"),
            name=kwargs.get("name")
        )

    def __repr__(self):
        return str(self)

    def __str__(self):
        return json.dumps(self._payload)


class Client():
    """Eligibility Verification API HTTP client."""

    def __init__(self, verifier, agency):
        self.url = verifier.api_url
        self.agency_id = agency.agency_id
        self.eligibility_types = list(verifier.eligibility_set() & agency.eligibility_set())

    def _tokenize(self, payload):
        """Create the request token."""
        return Token(agency=self.agency_id, eligibility=self.eligibility_types, **payload)

    def _auth_header(self, token):
        """Create an Authorization header for the request."""
        enc = str(base64.urlsafe_b64encode(bytes(str(token), "utf-8")), "utf-8")
        return dict(Authorization=f"Bearer {enc}")

    def _request(self, payload):
        """Make an API request for eligibility verification."""
        token = self._tokenize(payload)
        auth_header = self._auth_header(token)
        r = requests.get(self.url, headers=auth_header)
        return r.status_code, Response(r.json())

    def verify(self, sub, name):
        """Check eligibility for the subject and name."""
        payload = dict(sub=sub, name=name)
        return self._request(payload)


def verify(agency, sub, name):
    """Attempt eligibility verification, returning a tuple of lists (results, errors)."""

    responses = []
    errors = []

    for verifier in agency.eligibility_verifiers.all():
        result = Client(verifier, agency).verify(sub, name)
        if result and result[0] == 200:
            responses.append(result[1])
        elif result and result[0] != 200:
            errors.append(result[1])

    return responses, errors
