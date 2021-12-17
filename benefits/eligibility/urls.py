"""
The eligibility application: URLConf for the eligibility verification flow.
"""
from django.urls import path

from . import views


app_name = "eligibility"
urlpatterns = [
    # /eligibility
    path("", views.index, name="index"),
    path("confirm", views.confirm, name="confirm"),
    path("link/<agency:agency>/<uuid:uuid>", views.link, name="link"),
]
