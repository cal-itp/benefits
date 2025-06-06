from datetime import datetime
import json
import pytest

from benefits.enrollment.enrollment import Status
from benefits.enrollment_switchio.api import Registration, RegistrationStatus
from benefits.enrollment_switchio.enrollment import RegistrationResponse, RegistrationStatusResponse
from benefits.enrollment_switchio.session import Session
from benefits.enrollment_switchio.views import GatewayUrlView, IndexView


@pytest.fixture
def mocked_api_base_url(mocker):
    return mocker.patch(
        "benefits.enrollment_switchio.models.get_secret_by_name", return_value="https://example.com/backend-api"
    )


class TestIndexView:
    @pytest.fixture
    def view(self, app_request):
        """Fixture to create an instance of IndexView."""
        v = IndexView()
        v.setup(app_request)

        return v

    @pytest.mark.django_db
    @pytest.mark.usefixtures("mocked_session_flow")
    def test_get_context_data(self, view):

        context = view.get_context_data()

        assert "cta_button" in context
        assert "enrollment_method" in context
        assert "headline" in context
        assert "next_step" in context
        assert "partner_post_link" in context
        assert "alert_include" in context
        assert "transit_processor" in context.keys()
        transit_processor_context = context["transit_processor"]
        assert "name" in transit_processor_context
        assert "website" in transit_processor_context


class TestGatewayUrlView:
    @pytest.fixture
    def view(self, app_request):
        """Fixture to create an instance of GatewayUrlView."""
        v = GatewayUrlView()
        v.setup(app_request)

        return v

    @pytest.mark.django_db
    @pytest.mark.usefixtures("mocked_api_base_url", "mocked_session_agency")
    def test_get_gateway_url(self, view, app_request, mocker, model_TransitAgency, model_SwitchioConfig):
        model_TransitAgency.switchio_config = model_SwitchioConfig
        gateway_url = "https://example.com/cst/?regId=1234"
        mocker.patch(
            "benefits.enrollment_switchio.views.request_registration",
            return_value=RegistrationResponse(
                status=Status.SUCCESS, registration=Registration(regId="1234", gtwUrl=gateway_url)
            ),
        )

        response = view.get(app_request)

        assert response.status_code == 200
        assert json.loads(response.content) == {"gateway_url": gateway_url}

        session = Session(app_request)
        assert session.registration_id == "1234"
        assert session.gateway_url == gateway_url

    @pytest.mark.django_db
    @pytest.mark.usefixtures("mocked_api_base_url", "mocked_session_agency")
    def test_get_gateway_url_still_valid(self, view, app_request, mocker, model_TransitAgency, model_SwitchioConfig):
        model_TransitAgency.switchio_config = model_SwitchioConfig
        gateway_url = "https://example.com/cst/?regId=3456"
        mocked_request_registration = mocker.patch(
            "benefits.enrollment_switchio.views.request_registration",
            return_value=RegistrationResponse(
                status=Status.SUCCESS, registration=Registration(regId="3456", gtwUrl=gateway_url)
            ),
        )
        mocked_get_registration_status = mocker.patch(
            "benefits.enrollment_switchio.views.get_registration_status",
            return_value=RegistrationStatusResponse(
                status=Status.SUCCESS,
                registration_status=RegistrationStatus(
                    regState="created",
                    created=datetime.now(),
                    mode="register",
                    eshopResponseMode="form_post",
                    tokens=[],
                ),
            ),
        )
        Session(app_request, registration_id="3456", gateway_url=gateway_url)

        response = view.get(app_request)

        assert response.status_code == 200
        assert json.loads(response.content) == {"gateway_url": gateway_url}

        mocked_get_registration_status.assert_called_once()
        mocked_request_registration.assert_not_called()
        session = Session(app_request)
        assert session.registration_id == "3456"
        assert session.gateway_url == gateway_url

    @pytest.mark.django_db
    @pytest.mark.usefixtures("mocked_api_base_url", "mocked_session_agency")
    @pytest.mark.parametrize("regState", ["expired", "deleted"])
    def test_get_gateway_url_not_valid(self, view, app_request, mocker, model_TransitAgency, model_SwitchioConfig, regState):
        model_TransitAgency.switchio_config = model_SwitchioConfig
        gateway_url = "https://example.com/cst/?regId=7890"
        mocked_request_registration = mocker.patch(
            "benefits.enrollment_switchio.views.request_registration",
            return_value=RegistrationResponse(
                status=Status.SUCCESS, registration=Registration(regId="7890", gtwUrl=gateway_url)
            ),
        )
        mocked_get_registration_status = mocker.patch(
            "benefits.enrollment_switchio.views.get_registration_status",
            return_value=RegistrationStatusResponse(
                status=Status.SUCCESS,
                registration_status=RegistrationStatus(
                    regState=regState,
                    created=datetime.now(),
                    mode="register",
                    eshopResponseMode="form_post",
                    tokens=[],
                ),
            ),
        )
        Session(app_request, registration_id="1234 (expired ID)", gateway_url="https://example.com/cst/?regId=1234")

        response = view.get(app_request)

        assert response.status_code == 200
        assert json.loads(response.content) == {"gateway_url": gateway_url}

        mocked_get_registration_status.assert_called_once()
        mocked_request_registration.assert_called_once()
        session = Session(app_request)
        assert session.registration_id == "7890"
        assert session.gateway_url == gateway_url
