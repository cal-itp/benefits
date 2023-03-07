"""
The eligibility application: URLConf for the eligibility verification flow.
"""
from django.urls import path

from . import views


app_name = "eligibility"
urlpatterns = [
    # /eligibility
    path("", views.index, name="index"),
    path("<agency:agency>", views.index, name="agency_index"),
    path("start", views.start, name="start"),
    path("confirm", views.confirm, name="confirm"),
    path("unverified", views.unverified, name="unverified"),
]
