from django.urls import path

from . import views


app_name = "oauth"
urlpatterns = [
    # /oauth
    path("login", views.login, name="login"),
    path("authorize", views.authorize, name="authorize"),
    path("cancel", views.cancel, name="cancel"),
    path("logout", views.logout, name="logout"),
    path("post_logout", views.post_logout, name="post_logout"),
]
