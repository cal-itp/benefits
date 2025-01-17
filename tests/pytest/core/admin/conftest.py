import pytest


@pytest.fixture
def admin_request(admin_user, rf):
    def _admin_request(is_superuser=False):
        request = rf.get("/")
        request.user = admin_user
        admin_user.is_superuser = is_superuser
        return request

    return _admin_request
