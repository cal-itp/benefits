from cdt_identity.hooks import DefaultHooks
from django.shortcuts import redirect
import sentry_sdk

from benefits.routes import routes
from . import analytics


class OAuthHooks(DefaultHooks):
    @classmethod
    def pre_login(cls, request):
        super().pre_login(request)
        analytics.started_sign_in(request)

    @classmethod
    def system_error(cls, request, exception):
        super().system_error(request, exception)
        analytics.error(request, message=str(exception), operation="authorize_redirect")
        sentry_sdk.capture_exception(exception)
        return redirect(routes.OAUTH_SYSTEM_ERROR)
