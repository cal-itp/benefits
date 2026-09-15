import sentry_sdk
from cdt_identity.hooks import DefaultHooks
from django.shortcuts import redirect

from benefits.core import session

# from benefits.eligibility.views import analytics as eligibility_analytics
# from benefits.oauth import analytics


class OAuthHooks(DefaultHooks):
    @classmethod
    def pre_login(cls, request):
        super().pre_login(request)
        # analytics.started_sign_in(request)

    @classmethod
    def cancel_login(cls, request):
        super().cancel_login(request)
        # analytics.canceled_sign_in(request)
        return redirect("metro_mobility_wallet:eligbility_unverified")

    @classmethod
    def pre_logout(cls, request):
        super().pre_logout(request)
        # analytics.started_sign_out(request)

        # the user is signed out of the app
        session.logout(request)

    @classmethod
    def post_logout(cls, request):
        super().post_logout(request)
        # analytics.finished_sign_out(request)

        origin = session.origin(request)
        return redirect(origin)

    @classmethod
    def failure_to_proof(cls, request):
        super().failure_to_proof(request)
        session.update(request, logged_in=True)
        # QUESTION: Are they still considered "logged in" if they failed to prove?
        # Kegan thinks the only purpose of this may be to show the "log out of Login.gov" link

        # analytics.failure_to_proof(request)

        # Did they in fact "start eligibility", or does that only refer to the post-authentication piece?
        # flow = session.flow(request)
        # eligibility_analytics.started_eligibility(request, flow)

        return redirect("metro_mobility_wallet:failure_to_proof")

    @classmethod
    def claims_verified_eligible(cls, request, claims_request, claims_result):
        super().claims_verified_eligible(request, claims_request, claims_result)
        session.update(request, logged_in=True)
        # analytics.finished_sign_in(request)

        # flow = session.flow(request)
        # eligibility_analytics.started_eligibility(request, flow)

        session.update(request, eligible=True)
        # eligibility_analytics.returned_success(request, flow)

        return redirect("metro_mobility_wallet:enrollment_index")

    @classmethod
    def claims_verified_not_eligible(cls, request, claims_request, claims_result):
        super().claims_verified_not_eligible(request, claims_request, claims_result)
        session.update(request, logged_in=True)
        # analytics.finished_sign_in(request, error=claims_result.errors)

        # flow = session.flow(request)
        # eligibility_analytics.started_eligibility(request, flow)

        return redirect("metro_mobility_wallet:eligbility_unverified")

    @classmethod
    def system_error(cls, request, exception, operation):
        super().system_error(request, exception, operation)
        # analytics.error(request, message=str(exception), operation=str(operation))
        sentry_sdk.capture_exception(exception)
        return redirect("metro_mobility_wallet:system_error")
