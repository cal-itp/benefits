from django.urls import path

from . import views


app_name = "auth"
urlpatterns = [
    # /auth
    path("login", views.login, name="login"),
]
