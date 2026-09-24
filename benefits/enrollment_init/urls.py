from django.urls import path

from benefits.enrollment_init.views import IndexView, RegisterView

from .routes import routes

app_name = "init"
urlpatterns = [
    # /init/
    path("", IndexView.as_view(), name=routes.name(routes.ENROLLMENT_INIT_INDEX)),
    # /init/enrollment/card
    path("enrollment/card", RegisterView.as_view(), name=routes.name(routes.ENROLLMENT_INIT_REGISTER_CARD)),
]
