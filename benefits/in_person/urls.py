from django.urls import path

from benefits.routes import routes
from benefits.core.admin import admin
from . import views


app_name = "in_person"
urlpatterns = [
    path("eligibility/", admin.site.admin_view(views.eligibility), name=routes.name(routes.IN_PERSON_ELIGIBILITY)),
    path("enrollment/", admin.site.admin_view(views.enrollment), name=routes.name(routes.IN_PERSON_ENROLLMENT)),
]
