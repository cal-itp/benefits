from datetime import datetime, timedelta, timezone
import pytest

from benefits.core import session
from benefits.core.context_processors import unique_values, enrollment


def test_unique_values():
    original_list = ["a", "b", "c", "a", "a", "zzz", "b", "c", "d", "b"]

    new_list = unique_values(original_list)

    assert new_list == ["a", "b", "c", "zzz", "d"]


@pytest.mark.django_db
def test_enrollment_default(app_request):
    context = enrollment(app_request)

    assert "enrollment" in context
    assert context["enrollment"] == {"expires": None, "reenrollment": None, "supports_expiration": False}


@pytest.mark.django_db
def test_enrollment_expiration(app_request, model_EligibilityType_supports_expiration, model_TransitAgency):
    model_TransitAgency.eligibility_types.add(model_EligibilityType_supports_expiration)
    model_TransitAgency.save()

    expiry = datetime.now(tz=timezone.utc)
    reenrollment = expiry - timedelta(days=model_EligibilityType_supports_expiration.expiration_reenrollment_days)

    session.update(
        app_request,
        agency=model_TransitAgency,
        eligibility_types=[model_EligibilityType_supports_expiration.name],
        enrollment_expiry=expiry,
    )

    context = enrollment(app_request)

    assert context["enrollment"] == {"expires": expiry, "reenrollment": reenrollment, "supports_expiration": True}
