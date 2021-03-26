"""
The eligibility application: Eligibility Verification API implementation.
"""
import datetime
import json
import uuid

from jwcrypto import common as jwcrypto, jwe, jws, jwt
import requests

from benefits.settings import ALLOWED_HOSTS


class ApiError(Exception):
    """Error calling the Eligibility Verification API."""

    pass


class TokenError(Exception):
    """Error with API request/response token."""

    pass


class Token:
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
            name=name,
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


class TokenResponse:
    """Eligibility Verification API response token."""

    def __init__(self, response, agency, verifier):
        # read response token from body
        try:
            encrypted_signed_token = response.json()
        except ValueError:
            raise TokenError("Invalid response format")

        # decrypt using agency's private key
        allowed_algs = [verifier.jwe_encryption_alg, verifier.jwe_cek_enc]
        decrypted_token = jwe.JWE(algs=allowed_algs)
        try:
            decrypted_token.deserialize(encrypted_signed_token, key=agency.private_jwk)
        except jwe.InvalidJWEData:
            raise TokenError("Invalid JWE token")
        except jwe.InvalidJWEOperation:
            raise TokenError("JWE token decryption failed")

        decrypted_payload = str(decrypted_token.payload, "utf-8")

        # verify signature using verifier's public key
        signed_token = jws.JWS()
        try:
            signed_token.deserialize(decrypted_payload, key=verifier.public_jwk, alg=agency.jws_signing_alg)
        except jws.InvalidJWSObject:
            raise TokenError("Invalid JWS token")
        except jws.InvalidJWSSignature:
            raise TokenError("JWS token signature verification failed")

        # parse final payload and extract values
        payload = json.loads(str(signed_token.payload, "utf-8"))
        self.eligibility = list(payload.get("eligibility", []))
        self.error = payload.get("error", None)


class Client:
    """Eligibility Verification API HTTP client."""

    def __init__(self, agency):
        self.agency = agency
        self.verifier = agency.eligibility_verifier

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
        except jwcrypto.JWException:
            raise TokenError("Failed to tokenize form values")

        headers = self._auth_headers(token)

        try:
            r = requests.get(self.verifier.api_url, headers=headers)
            r.raise_for_status()
        except requests.ConnectionError:
            raise ApiError("Connection to verification server failed")
        except requests.Timeout:
            raise ApiError("Connection to verification server timed out")
        except requests.TooManyRedirects:
            raise ApiError("Too many redirects to verification server")
        except requests.HTTPError as e:
            raise ApiError(e)

        return TokenResponse(r, self.agency, self.verifier)

    def verify(self, sub, name):
        """Check eligibility for the subject and name."""
        return self._request(sub, name)
