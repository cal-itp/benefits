from django.urls import path

from . import views


app_name = "oauth"
urlpatterns = [
    # /oauth
    path("login", views.login, name="login"),
    path("authorize", views.authorize, name="authorize"),
    path("logout", views.logout, name="logout"),
]
