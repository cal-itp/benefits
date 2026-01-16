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

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests by treating them as GET requests.
        This prevents 405 errors when error handlers are triggered
        by failed POST submissions (common with CSRF failures).
        """
        return self.get(request, *args, **kwargs)


class BadRequestView(BaseErrorView):
    """View handler for HTTP 400 Bad Request responses."""

    status_code = 400


class ForbiddenView(BaseErrorView):
    """View handler for HTTP 403 Forbidden responses. Returns a 403 response with the BadRequest template."""

    status_code = 403
    template_name = "400.html"


class CsrfFailureView(BaseErrorView):
    """View handler for CSRF_FAILURE_VIEW. Returns a 403 response with the BadRequest template."""

    status_code = 403
    template_name = "400.html"


def csrf_failure_handler(request, reason=""):
    """Wrapper function to satisfy CSRF_FAILURE_VIEW string resolution."""
    return CsrfFailureView.as_view()(request, reason=reason)


class NotFoundView(BaseErrorView):
    """View handler for HTTP 404 Not Found responses."""

    status_code = 404


class ServerErrorView(BaseErrorView):
    """View handler for HTTP 500 Server Error responses."""

    status_code = 500


def server_error_handler(request):
    """Wrapper function to satisfy handler500 system check (urls.E007)."""
    return ServerErrorView.as_view()(request)
