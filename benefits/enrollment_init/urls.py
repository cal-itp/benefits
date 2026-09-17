from django.urls import path

from benefits.enrollment_init.views import IndexView
from benefits.routes import routes

app_name = "init"
urlpatterns = [
    # /init/
    path("", IndexView.as_view(), name=routes.name(routes.ENROLLMENT_INIT_INDEX)),
]
