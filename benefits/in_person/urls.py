from django.contrib import admin
from django.urls import path

from benefits.routes import routes
from . import views


app_name = "in_person"
urlpatterns = [
    path(
        "eligibility/", admin.site.admin_view(views.EligibilityView.as_view()), name=routes.name(routes.IN_PERSON_ELIGIBILITY)
    ),
    path("enrollment/", admin.site.admin_view(views.EnrollmentView.as_view()), name=routes.name(routes.IN_PERSON_ENROLLMENT)),
    path(
        "enrollment/error",
        admin.site.admin_view(views.system_error),
        name=routes.name(routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR),
    ),
    path(
        "enrollment/error/reenrollment",
        admin.site.admin_view(views.ReenrollmentErrorView.as_view()),
        name=routes.name(routes.IN_PERSON_ENROLLMENT_REENROLLMENT_ERROR),
    ),
    path(
        "enrollment/littlepay",
        admin.site.admin_view(views.LittlepayEnrollmentView.as_view()),
        name=routes.name(routes.IN_PERSON_ENROLLMENT_LITTLEPAY_INDEX),
    ),
    path(
        "enrollment/littlepay/token/",
        admin.site.admin_view(views.LittlepayTokenView.as_view()),
        name=routes.name(routes.IN_PERSON_ENROLLMENT_LITTLEPAY_TOKEN),
    ),
    path("enrollment/retry", admin.site.admin_view(views.retry), name=routes.name(routes.IN_PERSON_ENROLLMENT_RETRY)),
    path("enrollment/success", admin.site.admin_view(views.success), name=routes.name(routes.IN_PERSON_ENROLLMENT_SUCCESS)),
    path(
        "enrollment/switchio",
        admin.site.admin_view(views.SwitchioEnrollmentIndexView.as_view()),
        name=routes.name(routes.IN_PERSON_ENROLLMENT_SWITCHIO_INDEX),
    ),
    path(
        "enrollment/switchio/gateway_url",
        admin.site.admin_view(views.SwitchioGatewayUrlView.as_view()),
        name=routes.name(routes.IN_PERSON_ENROLLMENT_SWITCHIO_GATEWAY_URL),
    ),
    path("error/", admin.site.admin_view(views.server_error), name=routes.name(routes.IN_PERSON_SERVER_ERROR)),
]
