from django.urls import reverse

import pytest

from benefits.core import views
from benefits.routes import routes
from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.core.models import EnrollmentFlow
from benefits.core.views import (
    bad_request,
    csrf_failure,
    page_not_found,
    server_error,
)
import benefits.core.session


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

    def test_get_context_data(self, view, model_TransitAgency):
        context = view.get_context_data()

        for key, value in model_TransitAgency.index_context.items():
            assert context[key] == value


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

    def test_get(self, view, app_request):
        agency = view.kwargs["agency"]
        # recreate the condition of the live view, where the agency kwarg is passed to the get() call
        response = view.get(app_request, agency=agency)

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/plain"
        assert response.content.decode("utf-8") == agency.eligibility_api_public_key_data


@pytest.mark.django_db
class TestHelpView:
    @pytest.fixture
    def view(self, app_request):
        v = views.HelpView()
        v.setup(app_request)
        return v

    def test_view(self, view):
        assert view.template_name == "core/help.html"


@pytest.mark.django_db
class TestLoggedOutView:
    @pytest.fixture
    def view(self, app_request):
        v = views.LoggedOutView()
        v.setup(app_request)
        return v

    def test_view(self, view):
        assert view.template_name == "core/logged-out.html"


@pytest.mark.django_db
def test_bad_request_active_agency(app_request, mocked_session_agency, mocked_session_update):
    response = bad_request(app_request, Exception())

    assert response.status_code == 400
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == mocked_session_agency.return_value.index_url


@pytest.mark.django_db
def test_bad_request_no_active_agency(app_request, mocked_session_update):
    response = bad_request(app_request, Exception())

    assert response.status_code == 400
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == reverse(routes.INDEX)


@pytest.mark.django_db
def test_csrf_failure_active_agency(app_request, mocked_session_agency, mocked_session_update):
    response = csrf_failure(app_request, "reason")

    assert response.status_code == 404
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == mocked_session_agency.return_value.index_url


@pytest.mark.django_db
def test_csrf_failure_no_active_agency(app_request, mocked_session_update):
    response = csrf_failure(app_request, "reason")

    assert response.status_code == 404
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == reverse(routes.INDEX)


@pytest.mark.django_db
def test_not_found_active_agency(mocker, client, mocked_session_agency, mocked_session_update):
    response = client.get("/not-found")

    assert response.status_code == 404
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == mocked_session_agency.return_value.index_url


@pytest.mark.django_db
def test_not_found_no_active_agency(mocker, client, mocked_session_update):
    mocker.patch("benefits.core.session.active_agency", return_value=False)

    response = client.get("/not-found")

    assert response.status_code == 404
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == reverse(routes.INDEX)


@pytest.mark.django_db
def test_page_not_found(app_request):
    response = page_not_found(app_request, Exception())

    assert response.status_code == 404


@pytest.mark.django_db
def test_server_error(app_request):
    response = server_error(app_request)

    assert response.status_code == 500
