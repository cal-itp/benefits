from django.urls import path

from benefits.routes import routes
from benefits.enrollment_littlepay.views import IndexView, TokenView


app_name = "littlepay"
urlpatterns = [
    # /littlepay
    path("", IndexView.as_view(), name=routes.name(routes.ENROLLMENT_LITTLEPAY_INDEX)),
    path("token", TokenView.as_view(), name=routes.name(routes.ENROLLMENT_LITTLEPAY_TOKEN)),
]
