"""
Simple Test Eligibility Verification API Server.
"""
import datetime
import json
import re
import time

from flask import Flask
from flask_restful import Api, Resource, reqparse
from jwcrypto import jwe, jwk, jws, jwt


with open("./keys/server.key", "rb") as pemfile:
    server_private_key = jwk.JWK.from_pem(pemfile.read())
with open("./keys/client.pub", "rb") as pemfile:
    client_public_key = jwk.JWK.from_pem(pemfile.read())


class Database:
    """Simple hard-coded server database."""

    def __init__(self):
        with open("data/server.json") as f:
            data = json.load(f)
            self._config = data["config"]
            self._merchants = data["merchants"]
            self._users = data["users"]

    def check_merchant(self, merchant_id):
        """Check if the data matches a record in the database."""
        return merchant_id in self._merchants

    def check_user(self, key, user, types):
        """Check if the data matches a record in the database."""
        if (
            len(types) < 1
            or key not in self._users
            or self._users[key][0] != user
            or len(set(self._users[key][1]) & set(types)) < 1
        ):
            return []

        return list(set(self._users[key][1]) & set(types))

    @property
    def auth_header(self):
        return self._config["auth_header"]

    @property
    def auth_token(self):
        return self._config["auth_token"]

    @property
    def token_header(self):
        return self._config["token_header"]

    @property
    def jwe_cek_enc(self):
        return self._config["jwe_cek_enc"]

    @property
    def jwe_encryption_alg(self):
        return self._config["jwe_encryption_alg"]

    @property
    def jws_signing_alg(self):
        return self._config["jws_signing_alg"]

    @property
    def request_access(self):
        return self._config["request_access"]


app = Flask(__name__)
api = Api(app)


class MerchantAuthToken(Resource):

    db = Database()

    def _bad_request(self):
        return {"status": "400", "message": "Invalid request payload"}

    def _check_payload(self):
        """Ensure correct request payload"""
        req_parser = reqparse.RequestParser()
        req_parser.add_argument("request_access", required=True)
        args = req_parser.parse_args()

        if args.get("request_access") == self.db.request_access:
            return True
        else:
            return False

    def _not_found(self):
        return {"status": "404", "message": "Merchant doesn't exist"}

    def _token(self):
        return {"access_token": self.db.auth_token, "token_type": "Bearer", "expires_in": 60}

    def post(self, merchant_id):
        """Respond to an auth token request."""
        if self.db.check_merchant(merchant_id):
            if self._check_payload():
                return self._token(), 200
            else:
                return self._bad_request(), 400
        else:
            return self._not_found(), 404


class Verify(Resource):

    db = Database()

    def _check_headers(self):
        """Ensure correct request headers."""
        req_parser = reqparse.RequestParser()
        req_parser.add_argument(self.db.token_header, location="headers", required=True)
        req_parser.add_argument(self.db.auth_header, location="headers", required=True)
        headers = req_parser.parse_args()
        # verify auth_header's value
        if headers.get(self.db.auth_header) == self.db.auth_token:
            return headers
        else:
            return False

    def _get_token(self, headers):
        """Get the token from request headers"""
        token = headers.get(self.db.token_header, "").split(" ")
        if len(token) == 2:
            return token[1]
        elif len(token) == 1:
            return token[0]
        else:
            raise ValueError("Invalid token format")

    def _get_token_payload(self, token):
        """Decode a token (JWE(JWS))."""
        try:
            # decrypt
            decrypted_token = jwe.JWE(algs=[self.db.jwe_encryption_alg, self.db.jwe_cek_enc])
            decrypted_token.deserialize(token, key=server_private_key)
            decrypted_payload = str(decrypted_token.payload, "utf-8")
            # verify signature
            signed_token = jws.JWS()
            signed_token.deserialize(decrypted_payload, key=client_public_key, alg=self.db.jws_signing_alg)
            # return final payload
            payload = str(signed_token.payload, "utf-8")
            return json.loads(payload)
        except Exception:
            return False

    def _make_token(self, payload):
        """Wrap payload in a signed and encrypted JWT for response."""
        # sign the payload with server's private key
        header = {"typ": "JWS", "alg": self.db.jws_signing_alg}
        signed_token = jwt.JWT(header=header, claims=payload)
        signed_token.make_signed_token(server_private_key)
        signed_payload = signed_token.serialize()
        # encrypt the signed payload with client's public key
        header = {"typ": "JWE", "alg": self.db.jwe_encryption_alg, "enc": self.db.jwe_cek_enc}
        encrypted_token = jwt.JWT(header=header, claims=signed_payload)
        encrypted_token.make_encrypted_token(client_public_key)
        return encrypted_token.serialize()

    def get(self):
        """Respond to a verification request."""
        # introduce small fake delay
        time.sleep(2)

        headers = {}

        # verify required headers and API key check
        try:
            headers = self._check_headers()
        except Exception:
            return "Unauthorized", 403

        # parse inner payload from request token
        try:
            token = self._get_token(headers)
            token_payload = self._get_token_payload(token)
        except Exception as ex:
            return str(ex), 400

        if token_payload:
            try:
                # craft the response payload using parsed request token
                sub, name, eligibility = token_payload["sub"], token_payload["name"], list(token_payload["eligibility"])
                resp_payload = dict(
                    jti=token_payload["jti"],
                    iss=app.name,
                    iat=int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()),
                )
                # sub format check
                if re.match(r"^[A-Z]\d{7}$", sub):
                    # eligibility check against db
                    resp_payload["eligibility"] = self.db.check_user(sub, name, eligibility)
                    code = 200
                else:
                    resp_payload["error"] = {"sub": "invalid"}
                    code = 400
                # make a response token with appropriate response code
                return self._make_token(resp_payload), code
            except Exception as ex:
                return str(ex), 500
        else:
            return "Invalid token format", 400


api.add_resource(MerchantAuthToken, "/<merchant_id>/access-token")
api.add_resource(Verify, "/verify")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
