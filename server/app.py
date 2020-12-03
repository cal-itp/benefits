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
    """Simple hard-coded database of eligibility."""

    def __init__(self):
        with open("data/db.json") as f:
            self._USERS = json.load(f)

    def check(self, key, user, types):
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


app = Flask(__name__)
api = Api(app)


class Verify(Resource):
    auth_key = "Authorization"
    req_parser = reqparse.RequestParser()
    req_parser.add_argument(auth_key, location="headers", required=True)

    def _auth_token(self):
        """Get the bearer token from auth header."""
        args = self.req_parser.parse_args()
        token = args.get(self.auth_key, "")

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
        db = Database()
        token = self._auth_token()

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
