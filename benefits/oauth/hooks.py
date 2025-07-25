from cdt_identity.hooks import DefaultHooks
from django.shortcuts import redirect
from django.utils.decorators import method_decorator, decorator_from_middleware
import sentry_sdk

from benefits.routes import routes
from benefits.core import session
from benefits.core.middleware import AgencySessionRequired, FlowSessionRequired
from benefits.eligibility.views import VerifiedView, analytics as eligibility_analytics
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
    def post_logout(cls, request):
        super().post_logout(request)
        analytics.finished_sign_out(request)

        origin = session.origin(request)
        return redirect(origin)

    @classmethod
    @method_decorator(
        [
            decorator_from_middleware(AgencySessionRequired),
            decorator_from_middleware(FlowSessionRequired),
        ]
    )
    def claims_verified_eligible(cls, request, claims_request, claims_result):
        super().claims_verified_eligible(request, claims_request, claims_result)
        session.update(request, logged_in=True)
        analytics.finished_sign_in(request)

        flow = session.flow(request)
        eligibility_analytics.started_eligibility(request, flow)

        # changing the method to POST since this now represents a verification success
        # and we want to run the associated logic e.g. sending analytics events
        # GET requests to the VerifiedView simply redirect to enrollment index
        request.method = "POST"
        return VerifiedView().setup_and_dispatch(request)

    @classmethod
    @method_decorator(
        [
            decorator_from_middleware(AgencySessionRequired),
            decorator_from_middleware(FlowSessionRequired),
        ]
    )
    def claims_verified_not_eligible(cls, request, claims_request, claims_result):
        super().claims_verified_not_eligible(request, claims_request, claims_result)
        session.update(request, logged_in=True)
        analytics.finished_sign_in(request, error=claims_result.errors)

        flow = session.flow(request)
        eligibility_analytics.started_eligibility(request, flow)

        return redirect(routes.ELIGIBILITY_UNVERIFIED)

    @classmethod
    def system_error(cls, request, exception, operation):
        super().system_error(request, exception, operation)
        analytics.error(request, message=str(exception), operation=str(operation))
        sentry_sdk.capture_exception(exception)
        return redirect(routes.OAUTH_SYSTEM_ERROR)
