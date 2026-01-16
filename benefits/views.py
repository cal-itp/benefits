from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from benefits.core.middleware import index_or_agencyindex_origin_decorator, pageview_decorator


class BaseErrorView(TemplateView):
    """Base view class for HTTP error handlers."""

    status_code = 400

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_name = self.template_name or f"{self.status_code}.html"

    @method_decorator(pageview_decorator)
    @method_decorator(index_or_agencyindex_origin_decorator)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        """
        Inject the custom status code into the TemplateResponse.

        This is more idiomatic for CBVs than returning specialized subclasses
        (like HttpResponseNotFound), as it allows TemplateView to handle
        lazy rendering and context processors while ensuring the browser
        receives the correct error status.
        """
        response_kwargs.setdefault("status", self.status_code)
        return super().render_to_response(context, **response_kwargs)
