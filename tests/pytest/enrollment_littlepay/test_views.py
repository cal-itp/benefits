import time

import pytest
from authlib.integrations.base_client.errors import UnsupportedTokenTypeError
from django.urls import reverse
from requests import HTTPError

from benefits.routes import routes
from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.enrollment.enrollment import Status
from benefits.enrollment_littlepay.session import Session
from benefits.enrollment_littlepay.enrollment import CardTokenizationAccessResponse
import benefits.enrollment_littlepay.views


from benefits.enrollment_littlepay.views import IndexView


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.enrollment_littlepay.views)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.enrollment_littlepay.views, "sentry_sdk")


@pytest.fixture
def mocked_enrollment_result_handler():
    def handler(request, status, exception):
        return "success"

    return handler


@pytest.mark.django_db
def test_token_ineligible(client):
    path = reverse(routes.ENROLLMENT_LITTLEPAY_TOKEN)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_refresh(mocker, client):
    mocker.patch("benefits.enrollment_littlepay.session.Session.access_token_valid", return_value=False)

    mock_token = {}
    mock_token["access_token"] = "access_token"
    mock_token["expires_at"] = time.time() + 10000

    mocker.patch(
        "benefits.enrollment_littlepay.views.request_card_tokenization_access",
        return_value=CardTokenizationAccessResponse(
            Status.SUCCESS,
            access_token=mock_token["access_token"],
            expires_at=mock_token["expires_at"],
        ),
    )

    path = reverse(routes.ENROLLMENT_LITTLEPAY_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] == mock_token["access_token"]


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_valid(mocker, client):
    mocker.patch.object(Session, "access_token", "enrollment_token")
    mocker.patch("benefits.enrollment_littlepay.session.Session.access_token_valid", return_value=True)

    path = reverse(routes.ENROLLMENT_LITTLEPAY_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] == "enrollment_token"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_system_error(mocker, client, mocked_analytics_module, mocked_sentry_sdk_module):
    mocker.patch("benefits.enrollment_littlepay.session.Session.access_token_valid", return_value=False)

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=500, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(response=mock_error_response)

    mocker.patch(
        "benefits.enrollment_littlepay.views.request_card_tokenization_access",
        return_value=CardTokenizationAccessResponse(
            Status.SYSTEM_ERROR, access_token=None, expires_at=None, exception=http_error, status_code=500
        ),
    )

    path = reverse(routes.ENROLLMENT_LITTLEPAY_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" not in data
    assert "redirect" in data
    assert data["redirect"] == reverse(routes.ENROLLMENT_SYSTEM_ERROR)
    mocked_analytics_module.failed_access_token_request.assert_called_once()
    assert 500 in mocked_analytics_module.failed_access_token_request.call_args.args
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_http_error_400(mocker, client, mocked_analytics_module, mocked_sentry_sdk_module):
    mocker.patch("benefits.enrollment_littlepay.session.Session.access_token_valid", return_value=False)

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=400, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(response=mock_error_response)

    mocker.patch(
        "benefits.enrollment_littlepay.views.request_card_tokenization_access",
        return_value=CardTokenizationAccessResponse(
            Status.EXCEPTION, access_token=None, expires_at=None, exception=http_error, status_code=400
        ),
    )

    path = reverse(routes.ENROLLMENT_LITTLEPAY_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" not in data
    assert "redirect" in data
    assert data["redirect"] == reverse(routes.SERVER_ERROR)
    mocked_analytics_module.failed_access_token_request.assert_called_once()
    assert 400 in mocked_analytics_module.failed_access_token_request.call_args.args
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_misconfigured_client_id(mocker, client, mocked_analytics_module, mocked_sentry_sdk_module):
    mocker.patch("benefits.enrollment_littlepay.session.Session.access_token_valid", return_value=False)

    exception = UnsupportedTokenTypeError()

    mocker.patch(
        "benefits.enrollment_littlepay.views.request_card_tokenization_access",
        return_value=CardTokenizationAccessResponse(
            Status.EXCEPTION, access_token=None, expires_at=None, exception=exception, status_code=None
        ),
    )

    path = reverse(routes.ENROLLMENT_LITTLEPAY_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" not in data
    assert "redirect" in data
    assert data["redirect"] == reverse(routes.SERVER_ERROR)
    mocked_analytics_module.failed_access_token_request.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_connection_error(mocker, client, mocked_analytics_module, mocked_sentry_sdk_module):
    mocker.patch("benefits.enrollment_littlepay.session.Session.access_token_valid", return_value=False)

    exception = ConnectionError()

    mocker.patch(
        "benefits.enrollment_littlepay.views.request_card_tokenization_access",
        return_value=CardTokenizationAccessResponse(
            Status.EXCEPTION, access_token=None, expires_at=None, exception=exception, status_code=None
        ),
    )

    path = reverse(routes.ENROLLMENT_LITTLEPAY_TOKEN)
    response = client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" not in data
    assert "redirect" in data
    assert data["redirect"] == reverse(routes.SERVER_ERROR)
    mocked_analytics_module.failed_access_token_request.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


class TestIndexView:
    @pytest.fixture
    def view(self, app_request, mocked_enrollment_result_handler):
        """Fixture to create an instance of IndexView."""
        v = IndexView(enrollment_result_handler=mocked_enrollment_result_handler)
        v.setup(app_request)

        return v

    @pytest.mark.django_db
    @pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow")
    def test_get_context_data(self, view):
        context = view.get_context_data()

        assert "forms" in context
        assert "cta_button" in context
        assert "enrollment_method" in context
        assert "token_field" in context
        assert "form_retry" in context
        assert "form_server_error" in context
        assert "form_success" in context
        assert "form_system_error" in context
        assert "overlay_language" in context

        assert "headline" in context
        assert "next_step" in context
        assert "partner_post_link" in context
        assert "alert_include" in context

        assert "transit_processor" in context
        transit_processor_context = context["transit_processor"]
        assert "name" in transit_processor_context
        assert "website" in transit_processor_context
        assert "card_tokenize_url" in transit_processor_context
        assert "card_tokenize_env" in transit_processor_context

    def test_form_valid(self, mocker, view):
        mocker.patch("benefits.enrollment_littlepay.views.enroll", return_value=(Status.SUCCESS, None))

        form = view.form_class(data=dict(card_token="abc123"))
        handler_spy = mocker.spy(view, "enrollment_result_handler")

        assert form.is_valid()
        view.form_valid(form)

        handler_spy.assert_called_once_with(view.request, Status.SUCCESS, None)

    def test_form_invalid(self, view):
        with pytest.raises(Exception, match="Invalid card token form"):
            form = view.form_class()
            view.form_invalid(form)

    @pytest.mark.django_db
    @pytest.mark.usefixtures("mocked_session_eligible", "mocked_session_agency", "mocked_session_flow")
    def test_index_view(self, mocked_enrollment_result_handler, app_request):
        index_view = IndexView.as_view(enrollment_result_handler=mocked_enrollment_result_handler)
        response = index_view(app_request)

        assert response.status_code == 200
        assert response.template_name == ["enrollment_littlepay/index.html"]
