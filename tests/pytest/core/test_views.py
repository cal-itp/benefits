from django.urls import reverse

import pytest

from benefits.core.models import EligibilityVerifier, TransitAgency
import benefits.core.session
from benefits.core.views import (
    ROUTE_HELP,
    ROUTE_LOGGED_OUT,
    TEMPLATE_INDEX,
    bad_request,
    csrf_failure,
    page_not_found,
    server_error,
)
from benefits.core.middleware import ROUTE_INDEX


@pytest.fixture
def session_reset_spy(mocker):
    return mocker.spy(benefits.core.session, "reset")


@pytest.fixture
def mocked_active_agency(mocker):
    mock_agency = mocker.Mock()
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

    path = reverse(ROUTE_INDEX)
    response = client.get(path)

    assert response.status_code == 200
    assert "transit" in str(response.content)


@pytest.mark.django_db
def test_index_single_agency(mocker, model_TransitAgency, client, session_reset_spy):
    mocker.patch("benefits.core.models.TransitAgency.all_active", return_value=[model_TransitAgency])

    path = reverse(ROUTE_INDEX)
    response = client.get(path)

    session_reset_spy.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_INDEX


@pytest.mark.django_db
def test_agency_index_single_verifier(mocker, model_TransitAgency, client, session_reset_spy, mocked_session_update):
    mocker.patch("benefits.core.models.TransitAgency.all_active", return_value=[model_TransitAgency])

    response = client.get(model_TransitAgency.index_url)

    session_reset_spy.assert_called_once()
    mocked_session_update.assert_called_once()

    assert response.status_code == 200
    assert response.template_name == model_TransitAgency.index_template


@pytest.mark.django_db
def test_agency_index_multiple_verifier(
    mocker, model_TransitAgency, model_EligibilityVerifier, client, session_reset_spy, mocked_session_update
):
    # add another to the list of verifiers by cloning the original
    # https://stackoverflow.com/a/48149675/453168
    new_verifier = EligibilityVerifier.objects.get(pk=model_EligibilityVerifier.id)
    new_verifier.pk = None
    new_verifier.save()

    model_TransitAgency.eligibility_verifiers.add(new_verifier)
    mocker.patch("benefits.core.models.TransitAgency.all_active", return_value=[model_TransitAgency])

    response = client.get(model_TransitAgency.index_url)

    session_reset_spy.assert_called_once()
    mocked_session_update.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == model_TransitAgency.index_template


@pytest.mark.django_db
def test_agency_public_key(client, model_TransitAgency):
    response = client.get(model_TransitAgency.public_key_url)

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/plain"
    assert response.content.decode("utf-8") == model_TransitAgency.public_key_data


@pytest.mark.django_db
def test_help(client):
    path = reverse(ROUTE_HELP)

    response = client.get(path)

    assert response.status_code == 200
    assert "card" in str(response.content)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_help_with_session_agency(client):
    path = reverse(ROUTE_HELP)
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
    assert mocked_session_update.call_args.kwargs["origin"] == reverse(ROUTE_INDEX)


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
    assert mocked_session_update.call_args.kwargs["origin"] == reverse(ROUTE_INDEX)


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
    assert mocked_session_update.call_args.kwargs["origin"] == reverse(ROUTE_INDEX)


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
    path = reverse(ROUTE_LOGGED_OUT)
    response = client.get(path)

    assert response.status_code == 200
    assert "happybus" in str(response.content)
    assert "logged out" in str(response.content)
