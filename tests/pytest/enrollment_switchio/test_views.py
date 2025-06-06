import json
from django.urls import reverse
import pytest
from requests import HTTPError

from benefits.routes import routes
from benefits.enrollment.enrollment import Status
from benefits.enrollment_switchio.api import Registration
from benefits.enrollment_switchio.enrollment import RegistrationResponse
from benefits.enrollment_switchio.session import Session
import benefits.enrollment_switchio.views
from benefits.enrollment_switchio.views import GatewayUrlView, IndexView


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.enrollment_switchio.views)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.enrollment_switchio.views, "sentry_sdk")


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
    def view(self, app_request, mocked_session_agency):
        """Fixture to create an instance of GatewayUrlView."""
        v = GatewayUrlView()
        v.setup(app_request)
        v.agency = mocked_session_agency(app_request)

        return v

    @pytest.mark.django_db
    @pytest.mark.usefixtures("mocked_api_base_url")
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
    @pytest.mark.usefixtures("mocked_api_base_url")
    def test_get_gateway_url_system_error(
        self,
        view,
        app_request,
        mocker,
        model_TransitAgency,
        model_SwitchioConfig,
        mocked_analytics_module,
        mocked_sentry_sdk_module,
    ):
        mock_error = {"message": "Mock error message"}
        mock_error_response = mocker.Mock(status_code=500, **mock_error)
        mock_error_response.json.return_value = mock_error
        http_error = HTTPError(response=mock_error_response)

        model_TransitAgency.switchio_config = model_SwitchioConfig
        mocker.patch(
            "benefits.enrollment_switchio.views.request_registration",
            return_value=RegistrationResponse(
                status=Status.SYSTEM_ERROR,
                exception=http_error,
                status_code=http_error.response.status_code,
                registration=None,
            ),
        )

        response = view.get(app_request)

        assert response.status_code == 200
        assert json.loads(response.content) == {"redirect": reverse(routes.ENROLLMENT_SYSTEM_ERROR)}

        mocked_analytics_module.failed_pretokenization_request.assert_called_once()
        assert 500 in mocked_analytics_module.failed_pretokenization_request.call_args.args
        mocked_sentry_sdk_module.capture_exception.assert_called_once()

    @pytest.mark.django_db
    @pytest.mark.usefixtures("mocked_api_base_url")
    def test_get_gateway_url_http_error_400(
        self,
        view,
        app_request,
        mocker,
        model_TransitAgency,
        model_SwitchioConfig,
        mocked_analytics_module,
        mocked_sentry_sdk_module,
    ):
        mock_error = {"message": "Mock error message"}
        mock_error_response = mocker.Mock(status_code=400, **mock_error)
        mock_error_response.json.return_value = mock_error
        http_error = HTTPError(response=mock_error_response)

        model_TransitAgency.switchio_config = model_SwitchioConfig
        mocker.patch(
            "benefits.enrollment_switchio.views.request_registration",
            return_value=RegistrationResponse(
                status=Status.EXCEPTION,
                exception=http_error,
                status_code=http_error.response.status_code,
                registration=None,
            ),
        )

        response = view.get(app_request)

        assert response.status_code == 200
        assert json.loads(response.content) == {"redirect": reverse(routes.SERVER_ERROR)}

        mocked_analytics_module.failed_pretokenization_request.assert_called_once()
        assert 400 in mocked_analytics_module.failed_pretokenization_request.call_args.args
        mocked_sentry_sdk_module.capture_exception.assert_called_once()

    @pytest.mark.django_db
    @pytest.mark.usefixtures("mocked_api_base_url")
    def test_get_gateway_url_still_valid(self, view, app_request, mocker, model_TransitAgency, model_SwitchioConfig):
        model_TransitAgency.switchio_config = model_SwitchioConfig
        gateway_url = "https://example.com/cst/?regId=1234"
        Session(app_request, registration_id="1234", gateway_url=gateway_url)

        response = view.get(app_request)

        assert response.status_code == 200
        assert json.loads(response.content) == {"gateway_url": gateway_url}

        session = Session(app_request)
        assert session.registration_id == "1234"
        assert session.gateway_url == gateway_url
