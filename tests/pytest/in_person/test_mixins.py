from django.contrib.admin import site as admin_site
from django.views import View
import pytest

from benefits.in_person import mixins


class TestView(mixins.CommonContextMixin, View):
    pass


@pytest.mark.django_db
class TestCommonContextMixin:
    @pytest.fixture(autouse=True)
    def init(self, app_request, model_TransitAgency, model_User):
        app_request.user = model_User
        self.view = TestView()
        self.view.setup(app_request)
        self.view.agency = model_TransitAgency

    def test_get_context_data(self, app_request):
        ctx = self.view.get_context_data()

        title = ctx["title"]
        assert self.view.agency.long_name in title
        assert "In-person enrollment" in title
        assert admin_site.site_title in title

        admin_ctx = admin_site.each_context(app_request)
        for k in admin_ctx.keys():
            assert k in ctx
