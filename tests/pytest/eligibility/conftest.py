import pytest


@pytest.fixture
def mocked_eligibility_request_session(mocked_session_agency, mocked_session_verifier):
    """
    Stub fixture combines mocked_session_agency and mocked_session_verifier
    so session behaves like in normal requests to the eligibility app
    """
    pass
