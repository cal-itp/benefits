from datetime import datetime, timedelta, timezone
import pytest

from benefits.core import session
from benefits.core.context_processors import agency, enrollment, feature_flags, routes
from benefits.core.models import CardSchemes
from benefits.routes import routes as app_routes


@pytest.mark.django_db
def test_agency_no_session_agency(app_request):
    context = agency(app_request)

    assert context == {}


@pytest.mark.django_db
def test_agency_session_agency(app_request, mocked_session_agency):
    mocked_session_agency.return_value.supported_card_schemes = [CardSchemes.VISA, CardSchemes.AMEX]
    expected_card_schemes = [CardSchemes.CHOICES.get(CardSchemes.VISA), CardSchemes.CHOICES.get(CardSchemes.AMEX)]

    context = agency(app_request)

    mocked_session_agency.assert_called_once()
    assert "agency" in context

    agency_context = context["agency"]
    assert "eligibility_index_url" in agency_context
    assert "flows_help" in agency_context
    assert "info_url" in agency_context
    assert "littlepay_config" in agency_context
    assert "long_name" in agency_context
    assert "phone" in agency_context
    assert "short_name" in agency_context
    assert "slug" in agency_context
    assert agency_context["supported_card_schemes"] == expected_card_schemes
    assert "switchio_config" in agency_context


@pytest.mark.django_db
def test_enrollment_default(app_request):
    context = enrollment(app_request)

    assert "enrollment" in context
    assert context["enrollment"] == {"expires": None, "reenrollment": None, "supports_expiration": False}


@pytest.mark.parametrize("expected_flag", [True, False])
def test_feature_flags(app_request, settings, expected_flag):
    settings.LITTLEPAY_ADDITIONAL_CARDTYPES = expected_flag

    context = feature_flags(app_request)
    littlepay_flag = context["feature_flags"]["LITTLEPAY_ADDITIONAL_CARDTYPES"]

    assert littlepay_flag == expected_flag


@pytest.mark.django_db
def test_enrollment_expiration(app_request, model_EnrollmentFlow_supports_expiration):

    expiry = datetime.now(tz=timezone.utc)
    reenrollment = expiry - timedelta(days=model_EnrollmentFlow_supports_expiration.expiration_reenrollment_days)

    session.update(
        app_request,
        flow=model_EnrollmentFlow_supports_expiration,
        enrollment_expiry=expiry,
    )

    context = enrollment(app_request)

    assert context["enrollment"] == {"expires": expiry, "reenrollment": reenrollment, "supports_expiration": True}


@pytest.mark.django_db
def test_routes(app_request):
    app_routes_dict = app_routes.to_dict()

    context = routes(app_request)
    assert "routes" in context

    context_routes = context["routes"]
    for route_name in app_routes_dict.keys():
        assert route_name in context_routes
        assert context_routes[route_name] == app_routes_dict[route_name]
