"""
The metro_mobility_wallet application: URLConf for the metro_mobility_wallet app.
"""

from django.urls import path

from . import views

app_name = "metro_mobility_wallet"
urlpatterns = [
    # /metro-mobility-wallet
    path("", views.IndexView.as_view(), name="index"),
]
