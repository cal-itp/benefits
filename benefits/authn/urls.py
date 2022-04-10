from django.urls import path

from . import views


app_name = "authn"
urlpatterns = [
    # /auth
    path("login", views.login, name="login"),
    path("verify", views.verify, name="verify"),
]
