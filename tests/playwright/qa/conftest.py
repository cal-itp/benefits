import pytest


@pytest.fixture
def browser_context_args():
    return dict(user_agent="cal-itp/benefits-smoke-test")
