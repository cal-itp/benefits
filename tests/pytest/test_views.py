import pytest
from django.urls import reverse

from benefits import views
from benefits.routes import routes


@pytest.mark.django_db
class TestBaseErrorView:
    """Test the shared logic of the BaseErrorView."""

    @pytest.fixture
    def view(self, app_request):
        v = views.BaseErrorView()
        v.setup(app_request)
        return v

    def test_template_inference(self):
        v = views.BaseErrorView(status_code=420)
        assert v.template_name == "420.html"

    def test_dispatch__origin_decorator_active_agency(self, view, app_request, mocked_session_agency, mocked_session_update):
        """Verify index_or_agencyindex_origin_decorator updates origin with active agency."""
        agency = mocked_session_agency.return_value

        view.dispatch(app_request)

        # Verify session.update was called with the agency's index_url
        mocked_session_update.assert_any_call(app_request, origin=agency.index_url)

    def test_dispatch__origin_decorator_no_agency(self, view, app_request, mocker, mocked_session_update):
        """Verify index_or_agencyindex_origin_decorator defaults to INDEX route."""
        mocker.patch("benefits.core.session.active_agency", return_value=None)

        view.dispatch(app_request)

        # Verify session.update defaults to the root index path
        mocked_session_update.assert_any_call(app_request, origin=reverse(routes.INDEX))

    def test_dispatch__pageview_decorator(self, view, app_request, mocker):
        """Verify pageview_decorator triggers analytics event."""
        # patch the analytics module where it is USED (in middleware)
        # to ensure the middleware instance sees the mock
        mock_send = mocker.patch("benefits.core.middleware.analytics.send_event")

        # mock the event creation itself to ensure it doesn't
        # fail silently if app_request is missing analytics context.
        mock_event = mocker.patch("benefits.core.middleware.analytics.ViewedPageEvent").return_value

        # calling dispatch triggers the decorator chain
        response = view.dispatch(app_request)

        # TemplateResponses are lazy; rendering them ensures the
        # decorator's process_response logic is fully realized.
        if hasattr(response, "render"):
            response.render()

        mock_send.assert_called_once_with(mock_event)

    def test_render_to_response__injects_status(self, view):
        """Verifies the status code is correctly passed to the TemplateResponse."""
        view.status_code = 420
        response = view.render_to_response({})
        assert response.status_code == 420


@pytest.mark.django_db
class TestBadRequestView:
    @pytest.fixture
    def view(self, app_request):
        v = views.BadRequestView()
        v.setup(app_request)
        return v

    def test_view(self, view):
        assert view.status_code == 400
        assert view.template_name == "400.html"


@pytest.mark.django_db
class TestCsrfFailureView:
    @pytest.fixture
    def view(self, app_request):
        v = views.CsrfFailureView()
        v.setup(app_request)
        return v

    def test_view(self, view):
        assert view.status_code == 403
        # Verifying the explicit override
        assert view.template_name == "400.html"

    def test_handler_signature(self, app_request):
        # Verify the wrapper function used for CSRF_FAILURE_VIEW
        response = views.csrf_failure_handler(app_request, reason="Denied")
        assert response.status_code == 403
