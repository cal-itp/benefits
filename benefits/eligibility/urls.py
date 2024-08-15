"""
The eligibility application: URLConf for the eligibility verification flow.
"""

from django.urls import path

from benefits.routes import routes
from . import views


app_name = "eligibility"
urlpatterns = [
    # /eligibility
    path("", views.index, name=routes.name(routes.ELIGIBILITY_INDEX)),
    path("<agency:agency>", views.index, name=routes.name(routes.ELIGIBILITY_AGENCY_INDEX)),
    path("start", views.start, name=routes.name(routes.ELIGIBILITY_START)),
    path("confirm", views.confirm, name=routes.name(routes.ELIGIBILITY_CONFIRM)),
    path("unverified", views.unverified, name=routes.name(routes.ELIGIBILITY_UNVERIFIED)),
]
