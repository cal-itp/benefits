from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import pgettext, ugettext as _

from . import middleware, models, session, viewmodels


def _index_content_title():
    """Helper returns the content title for the common index page."""
    return _("core.index.content_title")


def _index_image():
    """Helper returns a viewmodels.Image for the common index page."""
    return viewmodels.Image("ridertappingbankcard.png", pgettext("image alt text", "core.index.image"))


def _index_paragraphs():
    """Helper returns the content paragraphs for the common index page."""
    return [_("core.index.p1"), _("core.index.p2"), _("core.index.p3")]


"""
Common PageViews for reuse
"""


class PageView:
    def accept(self, request, **kwargs):
        pass

    def render_page(self, **kwargs):
        return self.page


class IndexView(PageView):
    def __init__(self):
        # generate a button to the landing page for each active agency
        agencies = models.TransitAgency.all_active()
        buttons = [viewmodels.Button.outline_primary(text=a.short_name, url=a.index_url) for a in agencies]
        buttons[0].classes.append("mt-3")
        buttons[0].label = _("core.index.chooseprovider")

        self.page = viewmodels.Page(
            content_title=_index_content_title(),
            paragraphs=_index_paragraphs(),
            image=_index_image(),
            buttons=buttons,
            classes="home",
        )

    def accept(self, request, **kwargs):
        session.reset(request)


class AgencyIndexView(PageView):
    def __init__(self):
        self.page = viewmodels.Page(
            content_title=_index_content_title(),
            paragraphs=_index_paragraphs(),
            image=_index_image(),
            button=viewmodels.Button.primary(text=_("core.index.continue"), url=reverse("eligibility:index")),
            classes="home",
        )

    @method_decorator(middleware.pageview_decorator)
    def accept(self, request, **kwargs):
        session.reset(request)
        session.update(request, agency=kwargs["agency"], origin=kwargs["agency"].index_url)

    def render_page(self, **kwargs):
        return self.page


"""
Classes that define PageViews for specific agencies
"""


class AgencyPageViews:
    def get_initial_pageview(self):
        pass

    def get_pageview_from_slug(self, slug):
        pass


class Mst(AgencyPageViews):
    def get_initial_pageview(self):
        return AgencyIndexView()

    def get_pageview_from_slug(self, slug):
        pass


class Sacrt(AgencyPageViews):
    def get_initial_pageview(self):
        pageview = AgencyIndexView()
        pageview.page = viewmodels.Page(
            content_title=_index_content_title(),
            paragraphs=_index_paragraphs(),
            image=_index_image(),
            # text would come from i18n file of course. Just putting inline for now.
            button=viewmodels.Button.primary(text="Different text", url="types"),
            classes="home",
        )

        return pageview

    def get_pageview_from_slug(self, slug):
        # imagine a mapping of slugs to pages (here we're just always returning this one)
        pageview = PageView()
        pageview.page = viewmodels.Page(
            # text would come from i18n file of course. Just putting inline for now.
            content_title="This is a new page just for Sacrt",
            paragraphs=["This is a paragraph just for Sacrt", "This is another paragraph"],
            image=_index_image(),
            button=viewmodels.Button.primary(text=_("core.index.continue"), url=reverse("eligibility:index")),
            classes="home",
        )

        return pageview
