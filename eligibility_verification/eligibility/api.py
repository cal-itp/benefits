"""
The eligibility application: Eligiblity Verification API implementation.
"""
import random


def verify(form_data):
    print(form_data)
    return random.choice([True, False])
