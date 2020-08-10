"""
benefits URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
"""
from django.urls import include, path

from benefits.settings import ADMIN


handler400 = "benefits.core.views.bad_request"
handler404 = "benefits.core.views.page_not_found"
handler500 = "benefits.core.views.server_error"

urlpatterns = [
    path("", include("benefits.core.urls")),
    path("discounts/", include("benefits.discounts.urls")),
    path("eligibility/", include("benefits.eligibility.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]

if ADMIN:
    from django.contrib import admin
    urlpatterns.append(path("admin/", admin.site.urls))
