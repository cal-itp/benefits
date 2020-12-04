"""
The eligibility application: Eligibility Verification API implementation.
"""
import datetime
import json
import uuid

from jwcrypto import common as jwcrypto, jwe, jws, jwt
import requests

from eligibility_verification.settings import ALLOWED_HOSTS


class Token():
    """Eligibility Verification API request token."""

    def __init__(self, agency, verifier, sub, name):
        # compute the eligibility set for this token from agency and verifier
        eligibility = list(verifier.eligibility_set & agency.eligibility_set)

        # craft the main token payload
        payload = dict(
            jti=str(uuid.uuid4()),
            iss=ALLOWED_HOSTS[0],
            iat=int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()),
            agency=agency.agency_id,
            eligibility=eligibility,
            sub=sub,
            name=name
        )

        # sign the payload with agency's private key
        header = {"typ": "JWS", "alg": agency.jws_signing_alg}
        signed_token = jwt.JWT(header=header, claims=payload)
        signed_token.make_signed_token(agency.private_jwk)
        signed_payload = signed_token.serialize()

        # encrypt the signed payload with verifier's public key
        header = {"typ": "JWE", "alg": verifier.jwe_encryption_alg, "enc": verifier.jwe_cek_enc}
        encrypted_token = jwt.JWT(header=header, claims=signed_payload)
        encrypted_token.make_encrypted_token(verifier.public_jwk)

        # keep a reference to JWE
        self._jwe = encrypted_token

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self._jwe.serialize()


class Response():
    """Eligibility Verification API base response."""

    def __init__(self, status_code, error=None, message=None):
        self.status_code = status_code
        self.eligibility = []
        self._assign_error(error=error, message=message)

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.is_error():
            return json.dumps(self.error)
        else:
            return json.dumps(self.eligibility)

    def _assign_error(self, error=None, message=None):
        """Assign this Response's error attribute"""
        if not any([error, message]):
            return
        self.error = (message if not error else f"{message}: {str(error)}") if message else str(error)

    def is_verified(self):
        return len(self.eligibility) > 0

    def is_error(self):
        return self.error is not None

    def is_success(self):
        return self.status_code == 200


class TokenResponse(Response):
    """Eligibility Verification API response token."""

    def __init__(self, response, agency, verifier):
        super().__init__(response.status_code, message=response.text)

        # bail early for remote server errors
        if self.status_code >= 500:
            return

        # read response token from body
        try:
            encrypted_signed_token = response.json()
        except ValueError as ex:
            self._assign_error(ex, "Invalid response format")
            return

        # decrypt using agency's private key
        allowed_algs = [verifier.jwe_encryption_alg, verifier.jwe_cek_enc]
        decrypted_token = jwe.JWE(algs=allowed_algs)
        try:
            decrypted_token.deserialize(encrypted_signed_token, key=agency.private_jwk)
        except jwe.InvalidJWEData as ex:
            self._assign_error(ex, "Invalid JWE token")
            return
        except jwe.InvalidJWEOperation as ex:
            self._assign_error(ex, "JWE token decryption failed")
            return

        decrypted_payload = str(decrypted_token.payload, "utf-8")

        # verify signature using verifier's public key
        signed_token = jws.JWS()
        try:
            signed_token.deserialize(decrypted_payload, key=verifier.public_jwk, alg=agency.jws_signing_alg)
        except jws.InvalidJWSObject as ex:
            self._assign_error(ex, "Invalid JWS token")
            return
        except jws.InvalidJWSSignature as ex:
            self._assign_error(ex, "JWS token signature verification failed")
            return

        # parse final payload and extract values
        payload = json.loads(str(signed_token.payload, "utf-8"))
        self.eligibility = list(payload.get("eligibility", []))
        self.error = payload.get("error", None)


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
        try:
            token = self._tokenize(sub, name)
        except jwcrypto.JWException as ex:
            return Response(500, error=ex, message="Tokenize form values failed")

        try:
            headers = self._auth_headers(token)
        except Exception as ex:
            return Response(500, error=ex, message="Create auth headers failed")

        try:
            r = requests.get(self.verifier.api_url, headers=headers)
        except requests.ConnectionError as ex:
            return Response(500, error=ex, messages="Connection to verification server failed")
        except requests.Timeout as ex:
            return Response(500, error=ex, messages="Connection to verification server timed out")
        except requests.TooManyRedirects as ex:
            return Response(500, error=ex, messages="Too many redirects to verification server")

        return TokenResponse(response=r, agency=self.agency, verifier=self.verifier)

    def verify(self, sub, name):
        """Check eligibility for the subject and name."""
        return self._request(sub, name)


def verify(sub, name, agency):
    """Attempt eligibility verification, returning a tuple (verified_types: str[], errors: Response[])."""
    results = []
    errors = []
    # run through each verifier for this agency
    # TODO: probably not the best approach if there really are multiple verifiers
    for verifier in agency.eligibility_verifiers.all():
        # get a response, determine success/failure
        response = Client(agency=agency, verifier=verifier).verify(sub=sub, name=name)
        if response and response.is_success():
            results.append(response)
        elif response and response.is_error():
            errors.append(response)
    # return overall results and errors
    return _verified_types(results), errors


def _verified_types(results):
    """Return the list of distinct verified eligibility types using results from verify()."""
    return list(set([e for result in results for e in result.eligibility]))
