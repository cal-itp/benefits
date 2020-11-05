"""
The eligibility application: Eligibility Verification API implementation.
"""
import base64
import datetime
import json
import uuid

import requests

from eligibility_verification.core.models import TransitAgency
from eligibility_verification.settings import ALLOWED_HOSTS


class Response():
    """Eligibility Verification API response."""

    def __init__(self, status_code, token):
        token_bytes = bytes(token, "utf-8")
        dec = str(base64.urlsafe_b64decode(token_bytes), "utf-8")
        payload = json.loads(dec)

        self.eligibility = list(payload.get("eligibility", []))
        self.status_code = status_code
        self._payload = dict(
            jti=str(payload.get("jti")),
            iss=str(payload.get("iss")),
            iat=int(payload.get("iat")),
            eligibility=self.eligibility,
            error=json.loads(payload.get("error", "{}"))
        )

    def __repr__(self):
        return str(self)

    def __str__(self):
        return json.dumps(self._payload)

    def verified(self):
        return len(self._payload["eligibility"]) > 0

    def error(self):
        return self.status_code != 200

    def success(self):
        return self.status_code == 200


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
        return Response(r.status_code, r.json())

    def verify(self, sub, name):
        """Check eligibility for the subject and name."""
        payload = dict(sub=sub, name=name)
        return self._request(payload)


def verify(sub, name, agency=None):
    """Attempt eligibility verification, returning a tuple (verified_types: str[], results: Response[], errors: Response[])."""

    results = []
    errors = []
    agencies = TransitAgency.all_active() if agency is None else [agency]

    for agency in agencies:
        for verifier in agency.eligibility_verifiers.all():
            response = Client(verifier, agency).verify(sub, name)
            if response and response.success():
                results.append(response)
            elif response and response.error():
                errors.append(response)

    verified_types = _verified_types(results)

    return verified_types, results, errors


def _verified_types(results):
    """Return the list of distinct verified eligibility types using results from verify()."""
    return list(set([e for result in results for e in result.eligibility]))
