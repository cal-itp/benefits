from cdt_identity.hooks import DefaultHooks
from django.shortcuts import redirect
import sentry_sdk

from benefits.routes import routes
from benefits.core import session
from . import analytics


class OAuthHooks(DefaultHooks):
    @classmethod
    def pre_login(cls, request):
        super().pre_login(request)
        analytics.started_sign_in(request)

    @classmethod
    def cancel_login(cls, request):
        super().cancel_login(request)
        analytics.canceled_sign_in(request)
        return redirect(routes.ELIGIBILITY_UNVERIFIED)

    @classmethod
    def pre_logout(cls, request):
        super().pre_logout(request)
        analytics.started_sign_out(request)

        # the user is signed out of the app
        session.logout(request)

    @classmethod
    def system_error(cls, request, exception, operation):
        super().system_error(request, exception, operation)
        analytics.error(request, message=str(exception), operation=str(operation))
        sentry_sdk.capture_exception(exception)
        return redirect(routes.OAUTH_SYSTEM_ERROR)
