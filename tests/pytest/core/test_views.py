import pytest

import benefits.core.session
from benefits.core import views
from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.core.models import EnrollmentFlow
from benefits.core.models.common import PemData
from benefits.core.models.enrollment import EligibilityApiVerificationRequest
from benefits.routes import routes


@pytest.fixture
def session_reset_spy(mocker):
    return mocker.spy(benefits.core.session, "reset")


@pytest.mark.django_db
class TestIndexView:
    @pytest.fixture
    def view(self, app_request):
        v = views.IndexView()
        v.setup(app_request)
        return v

    def test_view(self, view):
        assert view.template_name == "core/index.html"

    def test_get(self, view, app_request, mocked_session_reset):
        response = view.get(app_request)

        assert response.status_code == 200
        mocked_session_reset.assert_called_once()

    def test_form_valid(self, view, model_TransitAgency):
        form = view.form_class(data=dict(select_transit_agency=model_TransitAgency.slug))

        assert form.is_valid()
        view.form_valid(form)
        assert view.success_url == model_TransitAgency.eligibility_index_url


@pytest.mark.django_db
class TestAgencyIndexView:
    @pytest.fixture
    def view(self, app_request, model_TransitAgency):
        v = views.AgencyIndexView()
        v.setup(app_request, agency=model_TransitAgency)
        return v

    def test_view(self, view):
        assert view.template_name == "core/index--agency.html"

    def test_get(self, view, app_request, mocked_session_reset, mocked_session_update):
        response = view.get(app_request)

        assert response.status_code == 200
        mocked_session_reset.assert_called_once()
        mocked_session_update.assert_called_once()


@pytest.mark.django_db
class TestAgencyCardView:
    @pytest.fixture
    def view(self, app_request, model_TransitAgency):
        v = views.AgencyCardView()
        v.setup(app_request, agency=model_TransitAgency)
        return v

    def test_view(self, view):
        assert view.pattern_name == routes.ELIGIBILITY_CONFIRM

    def test_get__with_one_eligibility_api_flow(
        self, view, app_request, mocked_session_reset, mocked_session_update, model_EnrollmentFlow_with_eligibility_api
    ):
        agency = view.kwargs["agency"]
        # recreate the condition of the live view, where the agency kwarg is passed to the get() call
        response = view.get(app_request, agency=agency)

        assert response.status_code == 302

        mocked_session_reset.assert_called_once()
        update_calls = mocked_session_update.mock_calls
        assert len(update_calls) == 2
        assert update_calls[0].kwargs["agency"] == agency
        assert update_calls[0].kwargs["origin"] == agency.index_url
        assert update_calls[1].kwargs["flow"] == model_EnrollmentFlow_with_eligibility_api

    def test_get__with_multiple_eligibility_api_flow(
        self, view, app_request, mocked_session_reset, mocked_session_update, model_EnrollmentFlow_with_eligibility_api
    ):
        agency = view.kwargs["agency"]
        # fake multiple Eligibility API flows for the agency
        new_flow = EnrollmentFlow.objects.get(pk=model_EnrollmentFlow_with_eligibility_api.id)
        new_flow.label = "New flow"
        new_flow.system_name = "senior"
        new_flow.pk = None
        new_flow.transit_agency = agency
        new_flow.save()

        # recreate the condition of the live view, where the agency kwarg is passed to the get() call
        response = view.get(app_request, agency=agency)

        assert response.status_code == 302
        mocked_session_reset.assert_called_once()
        assert mocked_session_update.mock_calls[1].kwargs["flow"] == new_flow

    def test_get__without_eligibility_api_flow(
        self, view, app_request, mocked_session_reset, mocked_session_update, model_EnrollmentFlow_with_scope_and_claim
    ):
        agency = view.kwargs["agency"]
        # we don't configure a flow with Eligibility API details
        model_EnrollmentFlow_with_scope_and_claim.transit_agency = agency
        model_EnrollmentFlow_with_scope_and_claim.save()

        # recreate the condition of the live view, where the agency kwarg is passed to the get() call
        response = view.get(app_request, agency=agency)

        assert response.status_code == 200
        assert response.template_name == TEMPLATE_USER_ERROR
        mocked_session_reset.assert_called_once()
        mocked_session_update.assert_called_once_with(app_request, agency=agency, origin=agency.index_url)


@pytest.mark.django_db
class TestAgencyEligibilityIndexView:
    @pytest.fixture
    def view(self, app_request, model_TransitAgency):
        v = views.AgencyEligibilityIndexView()
        v.setup(app_request, agency=model_TransitAgency)
        return v

    def test_view(self, view):
        assert view.pattern_name == routes.ELIGIBILITY_INDEX

    def test_get(self, view, app_request, mocked_session_reset, mocked_session_update):
        agency = view.kwargs["agency"]
        # recreate the condition of the live view, where the agency kwarg is passed to the get() call
        response = view.get(app_request, agency=agency)

        assert response.status_code == 302
        mocked_session_reset.assert_called_once()
        mocked_session_update.assert_called_once_with(app_request, agency=agency, origin=agency.index_url)


@pytest.mark.django_db
class TestAgencyPublicKeyView:

    @pytest.fixture
    def view(self, app_request, model_TransitAgency):
        v = views.AgencyPublicKeyView()
        v.setup(app_request, agency=model_TransitAgency)
        return v

    def test_get(self, view, app_request, model_EligibilityApiVerificationRequest):
        agency = view.kwargs["agency"]
        # recreate the condition of the live view, where the agency kwarg is passed to the get() call
        response = view.get(app_request, agency=agency)

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/plain"
        assert response.content.decode("utf-8") == model_EligibilityApiVerificationRequest.client_public_key_data

    def test_get_select_first_instance(self, view, app_request, model_EligibilityApiVerificationRequest):
        """
        Ensures that if multiple EligibilityApiVerificationRequest objects exist,
        the view returns the public key from the first one.
        """
        # Create a second verification request instance with different data
        public_key = PemData.objects.create(label="Test public key 2", text_secret_name="pem-secret-data-2")
        EligibilityApiVerificationRequest.objects.create(client_public_key=public_key, api_public_key=public_key)

        # Ensure we have more than one object in the DB
        assert EligibilityApiVerificationRequest.objects.count() > 1

        # The 'first' instance should be the one from the fixture
        expected_key = model_EligibilityApiVerificationRequest.client_public_key_data

        agency = view.kwargs["agency"]
        response = view.get(app_request, agency=agency)

        assert response.status_code == 200
        assert response.content.decode("utf-8") == expected_key


@pytest.mark.django_db
class TestHelpView:
    @pytest.fixture
    def view(self, app_request):
        v = views.HelpView()
        v.setup(app_request)
        return v

    def test_view(self, view):
        assert view.template_name == "core/help.html"

    def test_get_context_data_with_no_agency(self, view):
        context_data = view.get_context_data()
        assert "flows_help" not in context_data

    def test_get_context_data_with_agency(self, view, mocked_session_agency):
        context_data = view.get_context_data()
        assert "flows_help" in context_data


@pytest.mark.django_db
class TestLoggedOutView:
    @pytest.fixture
    def view(self, app_request):
        v = views.LoggedOutView()
        v.setup(app_request)
        return v

    def test_view(self, view):
        assert view.template_name == "core/logged-out.html"
