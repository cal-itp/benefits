import pytest


@pytest.fixture
def mocked_eligibility_request_session(mocked_session_agency, mocked_session_flow):
    """
    Stub fixture combines mocked_session_agency and mocked_session_flow
    so session behaves like in normal requests to the eligibility app
    """
    pass
