"""
The metro_mobility_wallet application: URLConf for the metro_mobility_wallet app.
"""

from cdt_identity import views as cdt_identity_views
from cdt_identity.routes import Routes
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
    # /metro-mobility-wallet/oauth/...
    path(f"oauth/{Routes.login}", decorator(cdt_identity_views.login), kwargs, name=Routes.login),
    path(f"oauth/{Routes.authorize}", decorator(cdt_identity_views.authorize), kwargs, name=Routes.authorize),
    path(f"oauth/{Routes.cancel}", decorator(cdt_identity_views.cancel), kwargs, name=Routes.cancel),
    path(
        f"oauth/{Routes.failure_to_proof}",
        decorator(cdt_identity_views.failure_to_proof),
        kwargs,
        name=Routes.failure_to_proof,
    ),
    path(f"oauth/{Routes.logout}", decorator(cdt_identity_views.logout), kwargs, name=Routes.logout),
    path(f"oauth/{Routes.post_logout}", decorator(cdt_identity_views.post_logout), kwargs, name=Routes.post_logout),
    path("oauth/error", views.SystemErrorView.as_view(), name=routes.name(routes.OAUTH_SYSTEM_ERROR)),
]
