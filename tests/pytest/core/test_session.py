import pytest

from benefits.core import session


@pytest.mark.django_db
def test_reset(rf):
    request = rf.get("/")

    request.session = {session._AGENCY: "abc"}

    session.reset(request)

    assert session.agency(request) is None
