"""
The enrollment application: URLConf for the benefits enrollment flow.
"""

from django.urls import path

from . import views


app_name = "enrollment"
urlpatterns = [
    # /enrollment
    path("", views.index, name="index"),
    path("token", views.token, name="token"),
    path("reenrollment-error", views.reenrollment_error, name="reenrollment-error"),
    path("retry", views.retry, name="retry"),
    path("success", views.success, name="success"),
    path("error", views.system_error, name="system-error"),
]
