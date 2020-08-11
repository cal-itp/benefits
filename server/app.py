import random

from flask import Flask
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)


class Verify(Resource):
    def get(self):
        return {"verified": random.choice([True, False])}


api.add_resource(Verify, "/verify")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
