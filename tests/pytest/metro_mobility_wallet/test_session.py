import pytest
from django.http import HttpRequest

from benefits.core.models.enrollment import EnrollmentFlow, SystemName
from benefits.metro_mobility_wallet.session import Session


@pytest.mark.django_db
class TestSession:
    @pytest.fixture
    def mock_request(self, mocker):
        request = mocker.MagicMock(spec=HttpRequest)
        request.session = {"session_id": 123}
        return request

    @pytest.fixture
    def model_metro_EnrollmentFlow(self):
        return EnrollmentFlow.objects.create(system_name=SystemName.METRO_MOBILITY_WALLET)

    def test_init(self, mock_request):
        session = Session(mock_request)
        assert session.request == mock_request
        assert session.session == mock_request.session

    def test_flow_no_metro_flow(self, mock_request):
        assert EnrollmentFlow.objects.filter(system_name=SystemName.METRO_MOBILITY_WALLET).count() == 0

        session = Session(mock_request)
        flow = session.flow

        assert flow is None

    def test_flow_metro_flow_exists(self, mock_request, model_metro_EnrollmentFlow):
        session = Session(mock_request)
        flow = session.flow

        assert flow == model_metro_EnrollmentFlow
