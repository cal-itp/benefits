"""
The enrollment application: URLConf for the benefits enrollment flow.
"""

from django.urls import path

from benefits.routes import routes
from . import views


app_name = "enrollment"
urlpatterns = [
    # /enrollment
    path("", views.index, name=routes.name(routes.ENROLLMENT_INDEX)),
    path("token", views.token, name=routes.name(routes.ENROLLMENT_TOKEN)),
    path("error/reenrollment", views.reenrollment_error, name=routes.name(routes.ENROLLMENT_REENROLLMENT_ERROR)),
    path("retry", views.retry, name=routes.name(routes.ENROLLMENT_RETRY)),
    path("success", views.success, name=routes.name(routes.ENROLLMENT_SUCCESS)),
    path("error", views.system_error, name=routes.name(routes.ENROLLMENT_SYSTEM_ERROR)),
]
