"""
The eligibility application: URLConf for the eligibility verification flow.
"""

from django.urls import path

from benefits.routes import routes
from . import views


app_name = "eligibility"
urlpatterns = [
    # /eligibility
    path("", views.IndexView.as_view(), name=routes.name(routes.ELIGIBILITY_INDEX)),
    path("start", views.start, name=routes.name(routes.ELIGIBILITY_START)),
    path("confirm", views.confirm, name=routes.name(routes.ELIGIBILITY_CONFIRM)),
    path("unverified", views.unverified, name=routes.name(routes.ELIGIBILITY_UNVERIFIED)),
]
