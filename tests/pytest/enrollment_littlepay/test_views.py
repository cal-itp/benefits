import pytest

from benefits.enrollment_littlepay.views import IndexView


class TestIndexView:
    @pytest.fixture
    def view(self, app_request):
        """Fixture to create an instance of IndexView."""
        v = IndexView()
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
