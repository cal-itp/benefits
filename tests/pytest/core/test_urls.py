"""
h/t to this blog post for the inspiration for these tests
https://adamj.eu/tech/2025/08/01/django-custom-url-converter-string/
"""

import pytest
from django.urls import path, reverse

# Import forces registration
from benefits.core.urls import TransitAgencyPathConverter  # noqa: F401

urlpatterns = [
    path(
        "<agency:agency>",
        lambda *args, **kwargs: None,  # dummy view
        name="sample",
    )
]
sample_path = urlpatterns[0]


@pytest.mark.django_db
class TestTransitAgencyPathConverter:
    def test_active_agency(self, model_TransitAgency):
        result = sample_path.resolve(model_TransitAgency.slug)
        assert result.kwargs["agency"] == model_TransitAgency

        result = reverse("sample", urlconf=__name__, kwargs={"agency": model_TransitAgency})
        assert result == f"/{model_TransitAgency.slug}"

    def test_active_agency__hyphen_slug(self, model_TransitAgency):
        model_TransitAgency.slug = "c-s-t"
        model_TransitAgency.save()

        result = sample_path.resolve(model_TransitAgency.slug)
        assert result.kwargs["agency"] == model_TransitAgency

        result = reverse("sample", urlconf=__name__, kwargs={"agency": model_TransitAgency})
        assert result == f"/{model_TransitAgency.slug}"

    def test_inactive_agency(self, model_TransitAgency_inactive):
        result = sample_path.resolve(model_TransitAgency_inactive.slug)
        assert result is None

    def test_unknown_agency(self):
        result = sample_path.resolve("unknown")
        assert result is None
