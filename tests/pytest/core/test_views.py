from django.urls import reverse

import pytest

from benefits.routes import routes
from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.core.models import EnrollmentFlow, TransitAgency
from benefits.core.views import (
    TEMPLATE_INDEX,
    bad_request,
    csrf_failure,
    page_not_found,
    server_error,
)
import benefits.core.session


@pytest.fixture
def session_reset_spy(mocker):
    return mocker.spy(benefits.core.session, "reset")


@pytest.fixture
def mocked_active_agency(mocker):
    mock_agency = mocker.Mock()

    # ensure agency.enrollment_flows is iterable
    mock_agency.enrollment_flows = mocker.MagicMock()

    mock_agency.index_url = "/agency"
    mocker.patch("benefits.core.session.agency", return_value=mock_agency)
    mocker.patch("benefits.core.session.active_agency", return_value=True)
    return mock_agency


@pytest.mark.django_db
def test_index_multiple_agencies(model_TransitAgency, client):
    # create another Transit Agency by cloning the original to ensure there are multiple
    # https://stackoverflow.com/a/48149675/453168
    new_agency = TransitAgency.objects.get(pk=model_TransitAgency.id)
    new_agency.pk = None
    new_agency.save()

    path = reverse(routes.INDEX)
    response = client.get(path)

    assert response.status_code == 200
    assert "transit" in str(response.content)


@pytest.mark.django_db
def test_index_single_agency(mocker, model_TransitAgency, client, session_reset_spy):
    mocker.patch("benefits.core.models.TransitAgency.all_active", return_value=[model_TransitAgency])

    path = reverse(routes.INDEX)
    response = client.get(path)

    session_reset_spy.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_INDEX


@pytest.mark.django_db
def test_agency_index_single_flow(mocker, model_TransitAgency, client, session_reset_spy, mocked_session_update):
    mocker.patch("benefits.core.models.TransitAgency.all_active", return_value=[model_TransitAgency])

    response = client.get(model_TransitAgency.index_url)

    session_reset_spy.assert_called_once()
    mocked_session_update.assert_called_once()

    assert response.status_code == 200
    assert response.template_name == "core/index--agency.html"


@pytest.mark.django_db
def test_agency_index_multiple_flow(
    mocker, model_TransitAgency, model_EnrollmentFlow, client, session_reset_spy, mocked_session_update
):
    # add another to the list of flows by cloning the original
    # https://stackoverflow.com/a/48149675/453168
    new_flow = EnrollmentFlow.objects.get(pk=model_EnrollmentFlow.id)
    new_flow.pk = None
    new_flow.save()

    model_TransitAgency.enrollment_flows.add(new_flow)
    mocker.patch("benefits.core.models.TransitAgency.all_active", return_value=[model_TransitAgency])

    response = client.get(model_TransitAgency.index_url)

    session_reset_spy.assert_called_once()
    mocked_session_update.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == "core/index--agency.html"


@pytest.mark.django_db
def test_agency_public_key(client, model_TransitAgency):
    url = reverse(routes.AGENCY_PUBLIC_KEY, args=[model_TransitAgency.slug])
    response = client.get(url)

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/plain"
    assert response.content.decode("utf-8") == model_TransitAgency.eligibility_api_public_key_data


@pytest.mark.django_db
def test_agency_card_with_eligibility_api_flow(
    client, model_TransitAgency, model_EnrollmentFlow_with_eligibility_api, mocked_session_update, mocked_session_reset
):
    url = reverse(routes.AGENCY_CARD, args=[model_TransitAgency.slug])
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse(routes.ELIGIBILITY_CONFIRM)

    mocked_session_reset.assert_called()
    update_calls = mocked_session_update.mock_calls
    assert len(update_calls) == 2
    assert update_calls[0].kwargs["agency"] == model_TransitAgency
    assert update_calls[0].kwargs["origin"] == model_TransitAgency.index_url
    assert update_calls[1].kwargs["flow"] == model_EnrollmentFlow_with_eligibility_api


@pytest.mark.django_db
def test_agency_card_with_multiple_eligibility_api_flows(
    client, model_TransitAgency, model_EnrollmentFlow_with_eligibility_api, mocked_session_update
):
    new_flow = EnrollmentFlow.objects.get(pk=model_EnrollmentFlow_with_eligibility_api.id)
    new_flow.label = "New flow"
    new_flow.system_name = "senior"
    new_flow.pk = None
    new_flow.transit_agency = model_TransitAgency
    new_flow.save()

    url = reverse(routes.AGENCY_CARD, args=[model_TransitAgency.slug])
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse(routes.ELIGIBILITY_CONFIRM)
    assert mocked_session_update.mock_calls[1].kwargs["flow"] == new_flow


@pytest.mark.django_db
def test_agency_card_without_eligibility_api_flow(
    client, model_TransitAgency, model_EnrollmentFlow_with_scope_and_claim, mocked_session_update, mocked_session_reset
):
    model_EnrollmentFlow_with_scope_and_claim.transit_agency = model_TransitAgency
    model_EnrollmentFlow_with_scope_and_claim.save()

    url = reverse(routes.AGENCY_CARD, args=[model_TransitAgency.slug])
    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR

    mocked_session_reset.assert_called()
    mocked_session_update.assert_called_once()
    assert mocked_session_update.mock_calls[0].kwargs["agency"] == model_TransitAgency
    assert mocked_session_update.mock_calls[0].kwargs["origin"] == model_TransitAgency.index_url


@pytest.mark.django_db
def test_agency_eligibility_index(client, model_TransitAgency, mocked_session_update):
    url = reverse(routes.AGENCY_ELIGIBILITY_INDEX, args=[model_TransitAgency.slug])
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse(routes.ELIGIBILITY_INDEX)
    mocked_session_update.assert_called_once()
    assert mocked_session_update.mock_calls[0].kwargs["agency"] == model_TransitAgency
    assert mocked_session_update.mock_calls[0].kwargs["origin"] == model_TransitAgency.index_url


@pytest.mark.django_db
def test_help(client):
    path = reverse(routes.HELP)

    response = client.get(path)

    assert response.status_code == 200
    assert "card" in str(response.content)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_help_with_session_agency(client):
    path = reverse(routes.HELP)
    response = client.get(path)

    assert response.status_code == 200


@pytest.mark.django_db
def test_bad_request_active_agency(app_request, mocked_active_agency, mocked_session_update):
    response = bad_request(app_request, Exception())

    assert response.status_code == 400
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == mocked_active_agency.index_url


@pytest.mark.django_db
def test_bad_request_no_active_agency(app_request, mocked_session_update):
    response = bad_request(app_request, Exception())

    assert response.status_code == 400
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == reverse(routes.INDEX)


@pytest.mark.django_db
def test_csrf_failure_active_agency(app_request, mocked_active_agency, mocked_session_update):
    response = csrf_failure(app_request, "reason")

    assert response.status_code == 404
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == mocked_active_agency.index_url


@pytest.mark.django_db
def test_csrf_failure_no_active_agency(app_request, mocked_session_update):
    response = csrf_failure(app_request, "reason")

    assert response.status_code == 404
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == reverse(routes.INDEX)


@pytest.mark.django_db
def test_not_found_active_agency(mocker, client, mocked_active_agency, mocked_session_update):
    response = client.get("/not-found")

    assert response.status_code == 404
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == mocked_active_agency.index_url


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


@pytest.mark.django_db
def test_logged_out(client):
    path = reverse(routes.LOGGED_OUT)
    response = client.get(path)

    assert response.status_code == 200
    assert "happybus" in str(response.content)
    assert "logged out" in str(response.content)
