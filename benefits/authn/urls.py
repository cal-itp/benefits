from django.urls import path

from . import views


app_name = "authn"
urlpatterns = [
    # /auth
    path("login", views.sign_in, name="login"),
    path("check", views.check, name="check"),
]
