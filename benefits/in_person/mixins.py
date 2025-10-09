from django.views.generic.base import ContextMixin
from django.contrib.admin import site as admin_site


class CommonContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        """Enrich context data with that common for all In-person views."""

        context = super().get_context_data(**kwargs)
        context.update(
            {
                **admin_site.each_context(self.request),
                "title": f"{self.agency.long_name} | In-person enrollment | {admin_site.site_title}",
            }
        )
        return context
