from django.urls import path

from benefits.routes import routes
from benefits.enrollment_littlepay.views import TokenView


app_name = "littlepay"
urlpatterns = [
    # /littlepay
    path("token", TokenView.as_view(), name=routes.name(routes.ENROLLMENT_LITTLEPAY_TOKEN)),
]
