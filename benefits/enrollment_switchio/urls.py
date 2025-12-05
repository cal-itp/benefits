from django.urls import path

from benefits.enrollment_switchio.views import GatewayUrlView, IndexView
from benefits.routes import routes

app_name = "switchio"
urlpatterns = [
    # /switchio
    path("", IndexView.as_view(), name=routes.name(routes.ENROLLMENT_SWITCHIO_INDEX)),
    path("gateway_url", GatewayUrlView.as_view(), name=routes.name(routes.ENROLLMENT_SWITCHIO_GATEWAY_URL)),
]
