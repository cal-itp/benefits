"""
The core application: URLConf for the root of the webapp.
"""
from django.urls import path, register_converter

from . import models, views


class TransitAgencyPathConverter():
    """Path converter to parse valid TransitAgency objects from URL paths."""

    regex = "[a-zA-Z]{3,5}"

    def to_python(self, value):
        agency = models.TransitAgency.get(value)
        if agency and agency.active:
            return agency
        else:
            raise ValueError()

    def to_url(self, value):
        return value.short_name


register_converter(TransitAgencyPathConverter, "agency")

app_name = "core"
urlpatterns = [
    # app root requires a valid agency reference
    path("<agency:agency>", views.index, name="index"),
    path("error", views.error, name="error")
]
