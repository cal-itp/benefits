import pytest

from benefits.enrollment_init.api import Client


class TestClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client(api_url="https://example.com", username="api_user", password="api_password")

    def test_init(self):
        assert self.client.authorization_header_value == "Basic YXBpX3VzZXI6YXBpX3Bhc3N3b3Jk"
