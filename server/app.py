"""
Simple Test Eligibility Verification API Server.
"""
import base64
import datetime
import json
import time

from flask import Flask
from flask_restful import Api, Resource, reqparse


class Database():
    """Simple hard-coded server database."""

    def __init__(self):
        with open("data/db.json") as f:
            data = json.load(f)
            self._AUTH = data["auth"]
            self._USERS = data["users"]

    def check_user(self, key, user, types):
        """Check if the data matches a record in the database."""
        if all((
            len(types) > 0,
            key in self._USERS,
            self._USERS[key][0] == user,
            len(set(self._USERS[key][1]) & set(types)) > 0
        )):
            return list(set(self._USERS[key][1]) & set(types))
        else:
            return []

    @property
    def auth_header(self):
        return self._AUTH["auth_header"]

    @property
    def auth_token(self):
        return self._AUTH["auth_token"]

    @property
    def token_header(self):
        return self._AUTH["token_header"]


app = Flask(__name__)
api = Api(app)


class Verify(Resource):

    db = Database()

    def _check_headers(self):
        """Ensure correct request headers."""
        req_parser = reqparse.RequestParser()
        req_parser.add_argument(self.db.token_header, location="headers", required=True)
        req_parser.add_argument(self.db.auth_header, location="headers", required=True)
        headers = req_parser.parse_args()

        if headers.get(self.db.auth_header) == self.db.auth_token:
            return headers
        else:
            return False

        if token.startswith("Bearer "):
            return token[len("Bearer "):]
        else:
            return False

    def _req_payload(self, token):
        """Decode a bearer token."""
        decoded_bytes = base64.urlsafe_b64decode(token)
        decoded_str = str(decoded_bytes, "utf-8")
        return json.loads(decoded_str)

    def get(self):
        """Respond to a verification request."""
        headers = {}

        try:
            headers = self._check_headers()
        except Exception as ex:
            return "Unauthorized", 403

        if token:
            data = self._req_payload(token)
            sub, name, eligibility = data["sub"], data["name"], list(data["eligibility"])
            payload = dict(
                jti=data["jti"],
                iss=app.name,
                iat=int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()),
                eligibility=db.check(sub, name, eligibility)
            )
        else:
            payload = {"errors": "Wrong Authorization header"}

        payload_bytes = bytes(json.dumps(payload), "utf-8")

        # introduce small fake delay
        time.sleep(2)

        return str(base64.urlsafe_b64encode(payload_bytes), "utf-8")


api.add_resource(Verify, "/verify")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
