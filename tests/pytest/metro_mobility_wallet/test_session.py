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
    def model_metro_EnrollmentFlow(self, model_IdentityGatewayConfig):
        return EnrollmentFlow.objects.create(
            system_name=SystemName.METRO_MOBILITY_WALLET, oauth_config=model_IdentityGatewayConfig
        )

    @pytest.mark.usefixtures("model_metro_EnrollmentFlow")
    def test_init(self, app_request, mocked_session_update):
        session = Session(app_request)

        mocked_session_update.assert_called_once_with(app_request, flow=session.flow)

    def test_flow_metro_flow_exists(self, mock_request, model_metro_EnrollmentFlow):
        session = Session(mock_request)
        flow = session.flow

        assert flow == model_metro_EnrollmentFlow

    @pytest.mark.usefixtures("model_metro_EnrollmentFlow")
    def test_accepted_terms_default(self, app_request):
        session = Session(app_request)

        assert session.accepted_terms is False

    @pytest.mark.usefixtures("model_metro_EnrollmentFlow")
    def test_accepted_terms_setter_and_getter(self, app_request):
        session = Session(app_request)

        session.accepted_terms = True

        assert session.accepted_terms is True
