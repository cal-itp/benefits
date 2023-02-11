"""
benefits URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
"""
import logging

from django.conf import settings
from django.urls import include, path

logger = logging.getLogger(__name__)

handler400 = "benefits.core.views.bad_request"
handler403 = "benefits.core.views.bad_request"
handler404 = "benefits.core.views.page_not_found"
handler500 = "benefits.core.views.server_error"


# based on
# https://docs.sentry.io/platforms/python/guides/django/#verify
def trigger_error(request):
    raise RuntimeError("Test error")


urlpatterns = [
    path("", include("benefits.core.urls")),
    path("eligibility/", include("benefits.eligibility.urls")),
    path("enrollment/", include("benefits.enrollment.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("oauth/", include("benefits.oauth.urls")),
    path("sentry-debug/", trigger_error),
]

if settings.ADMIN:
    from django.contrib import admin

    logger.debug("Register admin urls")
    urlpatterns.append(path("admin/", admin.site.urls))
else:
    logger.debug("Skip url registrations for admin")
