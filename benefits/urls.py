"""
benefits URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
"""
import logging

from django.urls import include, path

from benefits.settings import ADMIN


logger = logging.getLogger(__name__)

handler400 = "benefits.core.views.bad_request"
handler403 = "benefits.core.views.bad_request"
handler404 = "benefits.core.views.page_not_found"
handler500 = "benefits.core.views.server_error"

urlpatterns = [
    path("", include("benefits.core.urls")),
    path("enrollment/", include("benefits.enrollment.urls")),
    path("eligibility/", include("benefits.eligibility.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]

if ADMIN:
    from django.contrib import admin

    logger.debug("Register admin/ urls")
    urlpatterns.append(path("admin/", admin.site.urls))
else:
    logger.debug("Skip url registrations for admin")
