import base64
import datetime
import json

from flask import Flask, request
from flask_restful import Api, Resource, reqparse


auth_key = "Authorization"
req_parser = reqparse.RequestParser()
req_parser.add_argument(auth_key, location="headers", required=True)


def auth_token():
    """Get the bearer token from auth header."""
    args = req_parser.parse_args()
    token = args.get(auth_key, "")

    if token.startswith("Bearer "):
        return token[len("Bearer "):].trim()
    else:
        return False


def req_payload(token):
    """Decode a bearer token."""
    decoded_bytes = base64.urlsafe_b64decode(token)
    return json.loads(str(decoded_bytes, "utf-8"))


app = Flask(__name__)
api = Api(app)


class Verify(Resource):
    def get(self):
        token = auth_token()
        if token:
            data = req_payload(token)
            return {"verified": data}
        else:
            return {"error": "Wrong Authorization header"}


api.add_resource(Verify, "/verify")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
