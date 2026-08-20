import sentry_sdk
from cdt_identity.hooks import DefaultHooks
from django.shortcuts import redirect
from django.utils.decorators import decorator_from_middleware, method_decorator

from benefits.core import session
from benefits.core.middleware import FlowSessionRequired
from benefits.eligibility.views import analytics as eligibility_analytics
from benefits.oauth import analytics
from benefits.oauth.hooks import OAuthHooks as core_hooks


class OAuthHooks(DefaultHooks):
    # @classmethod
    # def pre_login(cls, request):
    #     super().pre_login(request)
    #     analytics.started_sign_in(request)
    pre_login = core_hooks.pre_login

    @classmethod
    def cancel_login(cls, request):
        super().cancel_login(request)
        analytics.canceled_sign_in(request)
        return redirect("metro_mobility_wallet:eligbility_unverified")

    # @classmethod
    # def pre_logout(cls, request):
    #     super().pre_logout(request)
    #     analytics.started_sign_out(request)

    #     # the user is signed out of the app
    #     session.logout(request)
    pre_logout = core_hooks.pre_logout

    # @classmethod
    # def post_logout(cls, request):
    #     super().post_logout(request)
    #     analytics.finished_sign_out(request)

    #     origin = session.origin(request)
    #     return redirect(origin)
    post_logout = core_hooks.post_logout

    @classmethod
    @method_decorator(
        [
            decorator_from_middleware(FlowSessionRequired),
        ]
    )
    def failure_to_proof(cls, request):
        super().failure_to_proof(request)
        session.update(request, logged_in=True)  # QUESTION: Are they still considered "logged in" if they failed to prove?
        analytics.failure_to_proof(request)

        # TODO: Confirm whether this event is desired.
        # Did they in fact "start eligibility", or does that only refer to the post-authentication piece?
        flow = session.flow(request)
        eligibility_analytics.started_eligibility(request, flow)

        return redirect("metro_mobility_wallet:failure_to_proof")

    @classmethod
    @method_decorator(
        [
            # decorator_from_middleware(AgencySessionRequired),
            decorator_from_middleware(FlowSessionRequired),
        ]
    )
    def claims_verified_eligible(cls, request, claims_request, claims_result):
        super().claims_verified_eligible(request, claims_request, claims_result)
        session.update(request, logged_in=True)
        analytics.finished_sign_in(request)

        flow = session.flow(request)
        eligibility_analytics.started_eligibility(request, flow)

        session.update(request, eligible=True)
        eligibility_analytics.returned_success(request, flow)

        return redirect("metro_mobility_wallet:enrollment_index")

    @classmethod
    @method_decorator(
        [
            # decorator_from_middleware(AgencySessionRequired),
            decorator_from_middleware(FlowSessionRequired),
        ]
    )
    def claims_verified_not_eligible(cls, request, claims_request, claims_result):
        super().claims_verified_not_eligible(request, claims_request, claims_result)
        session.update(request, logged_in=True)
        analytics.finished_sign_in(request, error=claims_result.errors)

        flow = session.flow(request)
        eligibility_analytics.started_eligibility(request, flow)

        return redirect("metro_mobility_wallet:eligbility_unverified")

    @classmethod
    def system_error(cls, request, exception, operation):
        super().system_error(request, exception, operation)
        analytics.error(request, message=str(exception), operation=str(operation))
        sentry_sdk.capture_exception(exception)
        return redirect("metro_mobility_wallet:system_error")
