"""
The metro_mobility_wallet application: URLConf for the metro_mobility_wallet app.
"""

from cdt_identity import views as cdt_identity_views
from cdt_identity.routes import Routes as OAuthRoutes
from django.urls import path
from django.utils.decorators import decorator_from_middleware

from benefits.oauth.middleware import FlowUsesClaimsVerificationSessionRequired
from benefits.routes import routes

from . import oauth, views

decorator = decorator_from_middleware(FlowUsesClaimsVerificationSessionRequired)
kwargs = {"hooks": oauth.OAuthHooks}

app_name = "metro_mobility_wallet"
urlpatterns = [
    # /metro-mobility-wallet/
    path("", views.IndexView.as_view(), name="index"),
    # /metro-mobility-wallet/eligibility/...
    path("eligibility", views.IndexView.as_view(), name="eligbility"),
    path("eligibility/start", views.EligibilityStartView.as_view(), name="eligbility_start"),
    path("eligibility/confirm", views.EligibilityConfirmView.as_view(), name="eligbility_confirm"),
    path("eligibility/unverified", views.EligibilityUnverifiedView.as_view(), name="eligbility_unverified"),
    # /metro-mobility-wallet/enrollment/...
    path("enrollment", views.IndexView.as_view(), name=routes.name("enrollment_index")),
    # path(
    #     "enrollment/error/reenrollment",
    #     views.ReenrollmentErrorView.as_view(),
    #     name=routes.name("enrollment_reenrollment_error"),
    # ),
    # path("enrollment/retry", views.RetryView.as_view(), name=routes.name("enrollment_retry")),
    # path("enrollment/success", views.SuccessView.as_view(), name=routes.name("enrollment_success")),
    # path("enrollment/error", views.SystemErrorView.as_view(), name=routes.name(routes.ENROLLMENT_SYSTEM_ERROR)),
    # /metro-mobility-wallet/oauth/...
    path(f"oauth/{OAuthRoutes.login}", decorator(cdt_identity_views.login), kwargs, name=OAuthRoutes.login),
    path(f"oauth/{OAuthRoutes.authorize}", decorator(cdt_identity_views.authorize), kwargs, name=OAuthRoutes.authorize),
    path(f"oauth/{OAuthRoutes.cancel}", decorator(cdt_identity_views.cancel), kwargs, name=OAuthRoutes.cancel),
    path(
        f"oauth/{OAuthRoutes.failure_to_proof}",
        decorator(cdt_identity_views.failure_to_proof),
        kwargs,
        name=OAuthRoutes.failure_to_proof,
    ),
    path(f"oauth/{OAuthRoutes.logout}", decorator(cdt_identity_views.logout), kwargs, name=OAuthRoutes.logout),
    path(f"oauth/{OAuthRoutes.post_logout}", decorator(cdt_identity_views.post_logout), kwargs, name=OAuthRoutes.post_logout),
    path("oauth/error", views.SystemErrorView.as_view(), name=routes.name(routes.OAUTH_SYSTEM_ERROR)),
]
