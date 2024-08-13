from django.urls import path

from benefits.core.admin import admin
from . import views


app_name = "in_person"
urlpatterns = [
    path("eligibility/", admin.site.admin_view(views.eligibility), name="eligibility"),
    path("enrollment/", admin.site.admin_view(views.enrollment), name="enrollment"),
]
