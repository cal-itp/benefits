"""
The metro_mobility_wallet application: URLConf for the metro_mobility_wallet app.
"""

from cdt_identity import views as cdt_identity_views
from cdt_identity.routes import Routes as OAuthRoutes
from django.urls import include, path
from django.utils.decorators import decorator_from_middleware

from benefits.oauth.middleware import FlowUsesClaimsVerificationSessionRequired
from benefits.routes import routes

from . import oauth, views

decorator = decorator_from_middleware(FlowUsesClaimsVerificationSessionRequired)
kwargs = {"hooks": oauth.OAuthHooks}

app_name = "metro_mobility_wallet"

oauth_patterns = [
    path(OAuthRoutes.login, decorator(cdt_identity_views.login), kwargs, name=OAuthRoutes.login),
    path(OAuthRoutes.authorize, decorator(cdt_identity_views.authorize), kwargs, name=OAuthRoutes.authorize),
    path(OAuthRoutes.cancel, decorator(cdt_identity_views.cancel), kwargs, name=OAuthRoutes.cancel),
    path(
        OAuthRoutes.failure_to_proof, decorator(cdt_identity_views.failure_to_proof), kwargs, name=OAuthRoutes.failure_to_proof
    ),
    path(OAuthRoutes.logout, decorator(cdt_identity_views.logout), kwargs, name=OAuthRoutes.logout),
    path(OAuthRoutes.post_logout, decorator(cdt_identity_views.post_logout), kwargs, name=OAuthRoutes.post_logout),
    path("error", views.SystemErrorView.as_view(), name=routes.name(routes.OAUTH_SYSTEM_ERROR)),
]

urlpatterns = [
    # /metro-mobility-wallet/
    path("", views.IndexView.as_view(), name="index"),
    #
    # This results in OAuth URLs in the form `metro-mobility-wallet/oauth/*` with names of `metro_mobility_wallet:cdt:*`
    path("oauth/", include((oauth_patterns, "cdt"), namespace="cdt")),
]
