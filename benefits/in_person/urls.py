from django.urls import path

from . import views


app_name = "in_person"
urlpatterns = [
    path("eligibility/", views.eligibility, name="eligibility"),
    path("enrollment/", views.enrollment, name="enrollment"),
]
