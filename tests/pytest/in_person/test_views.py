from django.urls import reverse

import pytest
from littlepay.api.funding_sources import FundingSourceResponse
from littlepay.api.groups import GroupFundingSourceResponse

from benefits.routes import routes


@pytest.fixture
def card_tokenize_form_data():
    return {"card_token": "tokenized_card"}


@pytest.fixture
def invalid_form_data():
    return {"invalid": "data"}


@pytest.fixture
def mocked_funding_source():
    return FundingSourceResponse(
        id="0",
        card_first_digits="0000",
        card_last_digits="0000",
        card_expiry_month="12",
        card_expiry_year="2024",
        card_scheme="visa",
        form_factor="physical",
        participant_id="cst",
        is_fpan=False,
        related_funding_sources=[],
    )


@pytest.fixture
def mocked_group_funding_source_no_expiry(mocked_funding_source):
    return GroupFundingSourceResponse(
        id=mocked_funding_source.id,
        created_date=None,
        updated_date=None,
        expiry_date=None,
    )


@pytest.mark.django_db
@pytest.mark.parametrize("viewname", [routes.IN_PERSON_ELIGIBILITY, routes.IN_PERSON_ENROLLMENT])
def test_view_not_logged_in(client, viewname):
    path = reverse(viewname)

    response = client.get(path)
    assert response.status_code == 302
    assert response.url == "/admin/login/?next=" + path


# admin_client is a fixture from pytest
# https://pytest-django.readthedocs.io/en/latest/helpers.html#admin-client-django-test-client-logged-in-as-admin
@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_eligibility_logged_in(admin_client):
    path = reverse(routes.IN_PERSON_ELIGIBILITY)

    response = admin_client.get(path)
    assert response.status_code == 200
    assert response.template_name == "in_person/eligibility.html"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_enrollment_logged_in_get(admin_client):
    path = reverse(routes.IN_PERSON_ENROLLMENT)

    response = admin_client.get(path)
    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment.html"
    assert "forms" in response.context_data
    assert "cta_button" in response.context_data
    assert "card_tokenize_env" in response.context_data
    assert "card_tokenize_func" in response.context_data
    assert "card_tokenize_url" in response.context_data
    assert "token_field" in response.context_data
    assert "form_retry" in response.context_data
    assert "form_success" in response.context_data
    assert "overlay_language" in response.context_data


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow")
def test_enrollment_logged_in_post_invalid_form(admin_client, invalid_form_data):
    path = reverse(routes.IN_PERSON_ENROLLMENT)

    with pytest.raises(Exception, match=r"form"):
        admin_client.post(path, invalid_form_data)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow")
def test_enrollment_logged_in_post_valid_form_success_does_not_support_expiration_no_expiry(
    mocker,
    admin_client,
    card_tokenize_form_data,
    model_EnrollmentFlow_does_not_support_expiration,
    mocked_funding_source,
):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    path = reverse(routes.IN_PERSON_ENROLLMENT)
    response = admin_client.post(path, card_tokenize_form_data)

    mock_client.link_concession_group_funding_source.assert_called_once_with(
        funding_source_id=mocked_funding_source.id, group_id=model_EnrollmentFlow_does_not_support_expiration.group_id
    )
    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/success.html"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow")
def test_enrollment_logged_in_post_valid_form_success_does_not_support_expiration_customer_already_enrolled_no_expiry(
    mocker,
    admin_client,
    card_tokenize_form_data,
    mocked_funding_source,
    mocked_group_funding_source_no_expiry,
):
    mock_client_cls = mocker.patch("benefits.enrollment.views.Client")
    mock_client = mock_client_cls.return_value
    mock_client.get_funding_source_by_token.return_value = mocked_funding_source

    mocker.patch("benefits.enrollment.views._get_group_funding_source", return_value=mocked_group_funding_source_no_expiry)

    path = reverse(routes.IN_PERSON_ENROLLMENT)
    response = admin_client.post(path, card_tokenize_form_data)

    mock_client.link_concession_group_funding_source.assert_not_called()

    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/success.html"
