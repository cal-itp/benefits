"""
The eligibility application: Eligibility Verification API implementation.
"""
import datetime
import json
import logging
import uuid

from jwcrypto import common as jwcrypto, jwe, jws, jwt
import requests

from benefits.settings import ALLOWED_HOSTS


logger = logging.getLogger(__name__)


class ApiError(Exception):
    """Error calling the Eligibility Verification API."""

    pass


class TokenError(Exception):
    """Error with API request/response token."""

    pass


class RequestToken:
    """Eligibility Verification API request token."""

    def __init__(self, agency, verifier, sub, name):
        logger.info("Initialize new request token")

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

        logger.debug("Sign token payload with agency's private key")
        header = {"typ": "JWS", "alg": agency.jws_signing_alg}
        signed_token = jwt.JWT(header=header, claims=payload)
        signed_token.make_signed_token(agency.private_jwk)
        signed_payload = signed_token.serialize()

        logger.debug("Encrypt signed token payload with verifier's public key")
        header = {"typ": "JWE", "alg": verifier.jwe_encryption_alg, "enc": verifier.jwe_cek_enc}
        encrypted_token = jwt.JWT(header=header, claims=signed_payload)
        encrypted_token.make_encrypted_token(verifier.public_jwk)

        logger.info("Signed and encrypted request token initialized")
        self._jwe = encrypted_token

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self._jwe.serialize()


class ResponseToken:
    """Eligibility Verification API response token."""

    def __init__(self, response, agency, verifier):
        logger.info("Read encrypted token from response")

        try:
            encrypted_signed_token = response.json()
        except ValueError:
            raise TokenError("Invalid response format")

        logger.debug("Decrypt response token using agency's private key")
        allowed_algs = [verifier.jwe_encryption_alg, verifier.jwe_cek_enc]
        decrypted_token = jwe.JWE(algs=allowed_algs)
        try:
            decrypted_token.deserialize(encrypted_signed_token, key=agency.private_jwk)
        except jwe.InvalidJWEData:
            raise TokenError("Invalid JWE token")
        except jwe.InvalidJWEOperation:
            raise TokenError("JWE token decryption failed")

        decrypted_payload = str(decrypted_token.payload, "utf-8")

        logger.debug("Verify decrypted response token's signature using verifier's public key")
        signed_token = jws.JWS()
        try:
            signed_token.deserialize(decrypted_payload, key=verifier.public_jwk, alg=agency.jws_signing_alg)
        except jws.InvalidJWSObject:
            raise TokenError("Invalid JWS token")
        except jws.InvalidJWSSignature:
            raise TokenError("JWS token signature verification failed")

        logger.info("Response token decrypted and signature verified")

        payload = json.loads(str(signed_token.payload, "utf-8"))
        self.eligibility = list(payload.get("eligibility", []))
        self.error = payload.get("error", None)


class Client:
    """Eligibility Verification API HTTP client."""

    def __init__(self, agency):
        logger.debug(f"Initialize client for agency: {agency.short_name}")
        self.agency = agency
        self.verifier = agency.eligibility_verifier

    def _tokenize_request(self, sub, name):
        """Create a request token."""
        return RequestToken(self.agency, self.verifier, sub, name)

    def _tokenize_response(self, response):
        """Parse a response token."""
        return ResponseToken(response, self.agency, self.verifier)

    def _auth_headers(self, token):
        """Create headers for the request with the token and verifier API keys"""
        headers = dict(Authorization=f"Bearer {token}")
        headers[self.verifier.api_auth_header] = self.verifier.api_auth_key
        return headers

    def _request(self, sub, name):
        """Make an API request for eligibility verification."""
        logger.debug("Start new eligibility verification request")

        try:
            token = self._tokenize_request(sub, name)
        except jwcrypto.JWException:
            raise TokenError("Failed to tokenize form values")

        try:
            logger.debug(f"GET request to {self.verifier.api_url}")
            r = requests.get(self.verifier.api_url, headers=self._auth_headers(token))
        except requests.ConnectionError:
            raise ApiError("Connection to verification server failed")
        except requests.Timeout:
            raise ApiError("Connection to verification server timed out")
        except requests.TooManyRedirects:
            raise ApiError("Too many redirects to verification server")
        except requests.HTTPError as e:
            raise ApiError(e)

        logger.debug("Process eligiblity verification response")
        return self._tokenize_response(r)

    def verify(self, sub, name):
        """Check eligibility for the subject and name."""
        return self._request(sub, name)
