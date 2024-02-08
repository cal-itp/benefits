"""
benefits URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
"""

import logging

from django.conf import settings
from django.http import HttpResponse
from django.urls import include, path

logger = logging.getLogger(__name__)

handler400 = "benefits.core.views.bad_request"
handler403 = "benefits.core.views.bad_request"
handler404 = "benefits.core.views.page_not_found"
handler500 = "benefits.core.views.server_error"

urlpatterns = [
    path("", include("benefits.core.urls")),
    path("eligibility/", include("benefits.eligibility.urls")),
    path("enrollment/", include("benefits.enrollment.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("oauth/", include("benefits.oauth.urls")),
]

if settings.DEBUG:
    # based on
    # https://docs.sentry.io/platforms/python/guides/django/#verify

    def trigger_error(request):
        raise RuntimeError("Test error")

    urlpatterns.append(path("error/", trigger_error))

    # simple route to read a pre-defined "secret"
    # this "secret" does not contain sensitive information
    # and is only configured in the dev environment for testing/debugging

    def test_secret(request):
        from benefits.secrets import get_secret_by_name

        return HttpResponse(get_secret_by_name("testsecret"))

    urlpatterns.append(path("testsecret/", test_secret))


if settings.ADMIN:
    from django.contrib import admin

    logger.debug("Register admin urls")
    urlpatterns.append(path("admin/", admin.site.urls))
    urlpatterns.append(path("google_sso/", include("django_google_sso.urls", namespace="django_google_sso")))
else:
    logger.debug("Skip url registrations for admin")
