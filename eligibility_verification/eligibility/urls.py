"""
The eligibility application: URLConf for the eligibility verification flow.
"""
from django.urls import path

from . import views


app_name = "eligibility"
urlpatterns = [
    # /eligiblity
    path("", views.index, name="index")
]
