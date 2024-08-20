from django.urls import path

from benefits.routes import routes
from . import views


app_name = "oauth"
urlpatterns = [
    # /oauth
    path("login", views.login, name=routes.name(routes.OAUTH_LOGIN)),
    path("authorize", views.authorize, name=routes.name(routes.OAUTH_AUTHORIZE)),
    path("cancel", views.cancel, name=routes.name(routes.OAUTH_CANCEL)),
    path("logout", views.logout, name=routes.name(routes.OAUTH_LOGOUT)),
    path("post_logout", views.post_logout, name=routes.name(routes.OAUTH_POST_LOGOUT)),
    path("error", views.system_error, name=routes.name(routes.OAUTH_SYSTEM_ERROR)),
]
