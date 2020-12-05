"""
The discounts application: URLConf for the discounts association flow.
"""
from django.urls import path

from . import views


app_name = "discounts"
urlpatterns = [
    # /discounts
    path("", views.index, name="index"),
    path("success", views.success, name="success"),
]
