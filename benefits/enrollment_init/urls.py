from django.urls import path

from benefits.enrollment_init.views import IndexView, StartView, SuccessView
from benefits.routes import routes

app_name = "init"
urlpatterns = [
    # /init/
    path("", IndexView.as_view(), name=routes.name(routes.ENROLLMENT_INIT_INDEX)),
    # /init/start
    path("start", StartView.as_view(), name=routes.name(routes.ENROLLMENT_INIT_START)),
    # /init/success
    path("success", SuccessView.as_view(), name=routes.name(routes.ENROLLMENT_INIT_SUCCESS)),
]
