"""
The core application: URLConf for the root of the webapp.
"""
from django.urls import path

from . import views


app_name = "core"
urlpatterns = [
    # website root
    path("", views.index, name="index"),
    path("error", views.error, name="error")
]
