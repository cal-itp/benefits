import pytest
from django.http import HttpRequest

from benefits.metro_mobility_wallet.session import Session


class TestSession:
    @pytest.fixture
    def mock_request(self, mocker):
        request = mocker.MagicMock(spec=HttpRequest)
        request.session = {"session_id": 123}
        return request

    def test_init(self, mock_request):
        session = Session(mock_request)
        assert session.request == mock_request
        assert session.session == mock_request.session
