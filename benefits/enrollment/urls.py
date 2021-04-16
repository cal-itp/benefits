"""
The enrollment application: URLConf for the benefits enrollment flow.
"""
from django.urls import path

from . import views


app_name = "enrollment"
urlpatterns = [
    # /enrollment
    path("", views.index, name="index"),
    path("retry", views.retry, name="retry"),
    path("success", views.success, name="success"),
]
