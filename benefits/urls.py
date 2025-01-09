"""
benefits URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

import logging
import re

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.views.static import serve

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
    path("in_person/", include("benefits.in_person.urls")),
]

# serve user-uploaded media files
#
# the helper function `django.conf.urls.static.static` mentioned in
# https://docs.djangoproject.com/en/5.1/howto/static-files/#serving-files-uploaded-by-a-user-during-development
# only works when settings.DEBUG = True, so here we add the URL pattern ourselves so it works regardless of DEBUG.
prefix = settings.MEDIA_URL
urlpatterns.extend(
    [re_path(r"^%s(?P<path>.*)$" % re.escape(prefix.lstrip("/")), serve, {"document_root": settings.MEDIA_ROOT})]
)

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

logger.debug("Register admin urls")
urlpatterns.append(path("admin/", admin.site.urls))
urlpatterns.append(path("google_sso/", include("django_google_sso.urls", namespace="django_google_sso")))
