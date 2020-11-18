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
        if self.is_error():
            return json.dumps(self.error)
        else:
            return json.dumps(self.eligibility)

    def is_verified(self):
        return len(self.eligibility) > 0

    def is_error(self):
        return self.error is not None

    def is_success(self):
        return self.status_code == 200


class Token():
    """Eligibility Verification API request token."""

    def __init__(self, agency, verifier, sub, name):
        # compute the eligibility set for this token from agency and verifier
        eligibility = list(verifier.eligibility_set() & agency.eligibility_set())
        # craft the main token payload
        self._payload = dict(
            jti=str(uuid.uuid4()),
            iss=ALLOWED_HOSTS[0],
            iat=int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()),
            agency=agency.agency_id,
            eligibility=eligibility,
            sub=sub,
            name=name
        )

    def __repr__(self):
        return str(self)

    def __str__(self):
        return json.dumps(self._payload)


class Client():
    """Eligibility Verification API HTTP client."""

    def __init__(self, agency, verifier):
        self.agency = agency
        self.verifier = verifier

    def _tokenize(self, sub, name):
        """Create the request token."""
        return Token(agency=self.agency, verifier=self.verifier, sub=sub, name=name)

    def _auth_headers(self, token):
        """Create headers for the request with the token and verifier API keys"""
        headers = dict(Authorization=f"Bearer {token}")
        headers[self.verifier.api_auth_header] = self.verifier.api_auth_key
        return headers

    def _request(self, sub, name):
        """Make an API request for eligibility verification."""
        token = self._tokenize(sub, name)
        headers = self._auth_headers(token)
        r = requests.get(self.verifier.api_url, headers=headers)
        return Response(r.status_code, r.json())

    def verify(self, sub, name):
        """Check eligibility for the subject and name."""
        return self._request(sub, name)


def verify(sub, name, agency):
    """Attempt eligibility verification, returning a tuple (verified_types: str[], errors: Response[])."""

    results = []
    errors = []

    for verifier in agency.eligibility_verifiers.all():
        response = Client(agency=agency, verifier=verifier).verify(sub=sub, name=name)
        if response and response.is_success():
            results.append(response)
        elif response and response.is_error():
            errors.append(response)

    return _verified_types(results), errors


def _verified_types(results):
    """Return the list of distinct verified eligibility types using results from verify()."""
    return list(set([e for result in results for e in result.eligibility]))
