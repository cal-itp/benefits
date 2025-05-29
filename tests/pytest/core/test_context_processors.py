from datetime import datetime, timedelta, timezone
import pytest

from benefits.routes import routes as app_routes
from benefits.core import session
from benefits.core.context_processors import unique_values, enrollment, feature_flags, routes


def test_unique_values():
    original_list = ["a", "b", "c", "a", "a", "zzz", "b", "c", "d", "b"]

    new_list = unique_values(original_list)

    assert new_list == ["a", "b", "c", "zzz", "d"]


@pytest.mark.django_db
def test_enrollment_default(app_request):
    context = enrollment(app_request)

    assert "enrollment" in context
    assert context["enrollment"] == {"expires": None, "reenrollment": None, "supports_expiration": False}


def test_feature_flags(app_request):
    context = feature_flags(app_request)
    littlepay_flag = context["feature_flags"]["LITTLEPAY_ADDITIONAL_CARDTYPES"]

    assert "feature_flags" in context
    assert isinstance(littlepay_flag, bool)


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
