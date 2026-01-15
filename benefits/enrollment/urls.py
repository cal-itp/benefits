"""
The enrollment application: URLConf for the benefits enrollment flow.
"""

from django.urls import path

from benefits.routes import routes

from . import views

app_name = "enrollment"
urlpatterns = [
    # /enrollment
    path("", views.IndexView.as_view(), name=routes.name(routes.ENROLLMENT_INDEX)),
    path("error/reenrollment", views.ReenrollmentErrorView.as_view(), name=routes.name(routes.ENROLLMENT_REENROLLMENT_ERROR)),
    path("retry", views.RetryView.as_view(), name=routes.name(routes.ENROLLMENT_RETRY)),
    path("success", views.SuccessView.as_view(), name=routes.name(routes.ENROLLMENT_SUCCESS)),
    path("error", views.SystemErrorView.as_view(), name=routes.name(routes.ENROLLMENT_SYSTEM_ERROR)),
]
