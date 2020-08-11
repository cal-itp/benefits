"""
The eligibility application: Eligiblity Verification API implementation.
"""
import random


class Client():
    def __init__(self, verifier, agency):
        self.url = verifier.api_url
        self.agency = agency

    def verify(self, sub, name):
        return random.choice([True, False])


def verify(sub, name, agency):
    for verifier in agency.eligibility_verifiers:
        client = Client(verifier, agency)
        if client.verify(sub, name):
            return True

    print("Tried all verifiers")
    return False
