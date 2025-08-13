from django.contrib import admin
from django.urls import path

from benefits.routes import routes
from . import views


app_name = "in_person"
urlpatterns = [
    path(
        "eligibility/", admin.site.admin_view(views.EligibilityView.as_view()), name=routes.name(routes.IN_PERSON_ELIGIBILITY)
    ),
    path("token/", admin.site.admin_view(views.token), name=routes.name(routes.IN_PERSON_ENROLLMENT_TOKEN)),
    path("enrollment/", admin.site.admin_view(views.EnrollmentView.as_view()), name=routes.name(routes.IN_PERSON_ENROLLMENT)),
    path(
        "enrollment/littlepay",
        admin.site.admin_view(views.enrollment),
        name=routes.name(routes.IN_PERSON_ENROLLMENT_LITTLEPAY_INDEX),
    ),
    path(
        "enrollment/switchio",
        admin.site.admin_view(views.enrollment),
        name=routes.name(routes.IN_PERSON_ENROLLMENT_SWITCHIO_INDEX),
    ),
    path(
        "enrollment/error/reenrollment",
        admin.site.admin_view(views.reenrollment_error),
        name=routes.name(routes.IN_PERSON_ENROLLMENT_REENROLLMENT_ERROR),
    ),
    path("enrollment/retry", admin.site.admin_view(views.retry), name=routes.name(routes.IN_PERSON_ENROLLMENT_RETRY)),
    path("enrollment/success", admin.site.admin_view(views.success), name=routes.name(routes.IN_PERSON_ENROLLMENT_SUCCESS)),
    path(
        "enrollment/error",
        admin.site.admin_view(views.system_error),
        name=routes.name(routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR),
    ),
    path("error/", admin.site.admin_view(views.server_error), name=routes.name(routes.IN_PERSON_SERVER_ERROR)),
]
