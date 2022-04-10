from django.urls import path

from . import views


app_name = "oauth"
urlpatterns = [
    # /oauth
    path("login", views.login, name="login"),
    path("verify", views.verify, name="verify"),
]
