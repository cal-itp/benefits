"""
The core application: view model definitions for the root of the webapp.
"""
from django.utils.translation import pgettext, gettext_lazy as _
from django.urls import reverse

from benefits.core import models

from . import session


class Button:
    """
    Represents a clickable button as styled <a> element (with optional label, optional transparent fallback text):
    * classes: str, str[]
    * id: str
    * fallback_text: str
    * label: str
    * text: str
    * url: str
    * target: str
    * rel: str
    """

    def __init__(self, **kwargs):
        classes = kwargs.get("classes", [])
        if isinstance(classes, str):
            classes = classes.split()

        self.classes = ["btn", "btn-lg"]
        self.classes.extend(classes)
        self.id = kwargs.get("id")
        self.fallback_text = kwargs.get("fallback_text")
        self.label = kwargs.get("label")
        self.text = kwargs.get("text", "Button")
        self.url = kwargs.get("url")
        self.target = kwargs.get("target")
        self.rel = kwargs.get("rel")

    @staticmethod
    def agency_contact_links(agency):
        """Create link buttons for agency contact information."""
        return [
            Button.link(label=agency.long_name, text=agency.phone, url=f"tel:{agency.phone}"),
            Button.link(text=agency.info_url, url=agency.info_url, target="_blank", rel="noopener noreferrer"),
        ]

    @staticmethod
    def home(request, text=None):
        """Create a button back to this session's origin."""
        if text is None:
            text = _("core.buttons.return_home")

        return Button.primary(text=text, url=session.origin(request))

    @staticmethod
    def link(**kwargs):
        classes = kwargs.pop("classes", [])
        if isinstance(classes, str):
            classes = classes.split(" ")
        classes.insert(0, "btn-link")
        return Button(classes=classes, **kwargs)

    @staticmethod
    def primary(**kwargs):
        classes = kwargs.pop("classes", [])
        if isinstance(classes, str):
            classes = classes.split(" ")
        classes.insert(0, "btn-primary")
        return Button(classes=classes, **kwargs)

    @staticmethod
    def outline_primary(**kwargs):
        classes = kwargs.pop("classes", [])
        if isinstance(classes, str):
            classes = classes.split(" ")
        classes.insert(0, "btn-outline-primary")
        return Button(classes=classes, **kwargs)

    @staticmethod
    def login(**kwargs):
        """Create a login.gov button, with a login.gov logo and fallback text"""
        btn = Button.primary(fallback_text="Login.gov", id="login", **kwargs)
        return btn

    @staticmethod
    def logout(**kwargs):
        """Create a button that logs user out, with a login.gov button, with a login.gov logo and fallback text"""
        btn = Button.primary(fallback_text="Login.gov", id="login", url=reverse("oauth:logout"), text="", **kwargs)
        return btn

    @staticmethod
    def previous_page(url):
        return Button(text=_("core.buttons.previous_page"), url=url)


class Icon:
    """Represents an icon."""

    def __init__(self, icon, alt):
        self.src = f"img/icon/{icon}.svg"
        self.alt = alt


class MediaItem:
    """
    Represents a media item in a list of items:
    * icon: core.viewmodels.Icon
    * details: str, str[]
    * heading: str
    """

    def __init__(self, icon: Icon, details, heading=None):
        self.icon = icon
        if isinstance(details, str):
            self.details = [details]
        elif isinstance(details, list):
            self.details = details
        else:
            self.details = [str(details)]
        self.heading = heading


class Modal:
    """
    Represents a modal dialog, triggered by a button:
    * id: str
    * aria_labelledby_id: str
    * button_text: str
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.aria_labelledby_id = kwargs.get("aria_labelledby_id")
        self.button_text = kwargs.get("button_text")


class AgencySelector(Modal):
    """
    Represents the agency selector modal dialog.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agencies = [TransitAgency(a) for a in models.TransitAgency.all_active()]


class Page:
    """
    Represents a page of content:
    * title: str
    * icon: core.viewmodels.Icon
    * headline: str
    * paragraphs: str[]
    * form: django.forms.Form
    * forms: django.forms.Form[]
    * button: core.viewmodels.Button
    * buttons: core.viewmodels.Button[]
    * modal: core.viewmodels.Modal
    * classes: str[]
    """

    def __init__(self, **kwargs):
        title = kwargs.get("title")
        if title is not None:
            self.title = title
        self.icon = kwargs.get("icon")
        self.headline = kwargs.get("headline")
        self.paragraphs = kwargs.get("paragraphs", [])
        self.steps = kwargs.get("steps")

        self.forms = kwargs.get("forms", [])
        if not isinstance(self.forms, list):
            self.forms = [self.forms]
        if "form" in kwargs:
            self.forms.append(kwargs.get("form"))

        self.buttons = kwargs.get("buttons", [])
        if not isinstance(self.buttons, list):
            self.buttons = [self.buttons]
        if "button" in kwargs:
            self.buttons.append(kwargs.get("button"))

        if "modal" in kwargs:
            self.modal = kwargs.get("modal")

        self.classes = kwargs.get("classes", [])
        if not isinstance(self.classes, list):
            self.classes = self.classes.split(" ")

    def context_dict(self):
        """Return a context dict for a Page."""
        return {"page": self}


class ErrorPage(Page):
    """
    Represents an error page:
    * title: str
    * icon: core.viewmodels.Icon
    * headline: str
    * paragraphs: str[]
    * button: core.viewmodels.Button
    """

    def __init__(self, **kwargs):
        super().__init__(
            title=kwargs.get("title", _("core.pages.error.title")),
            icon=kwargs.get("icon", Icon("sadbus", pgettext("image alt text", "core.icons.sadbus"))),
            headline=kwargs.get("headline", _("core.pages.error.title")),
            paragraphs=kwargs.get("paragraphs", [_("core.pages.server_error.headline")]),
            button=kwargs.get("button"),
        )

    @staticmethod
    def user_error(
        title=_("core.pages.user_error.title"),
        headline=_("core.pages.user_error.headline"),
        paragraphs=[_("core.pages.user_error.p[0]")],
        **kwargs,
    ):
        """Create a new core.viewmodels.ErrorPage instance with defaults for a user error."""
        return ErrorPage(title=title, headline=headline, paragraphs=paragraphs, **kwargs)

    @staticmethod
    def server_error(
        title=_("core.pages.server_error.title"),
        headline=_("core.pages.server_error.title"),
        paragraphs=[_("core.pages.server_error.p[0]")],
        **kwargs,
    ):
        """Create a new core.viewmodels.ErrorPage instance with defaults for a generic server error."""
        return ErrorPage(title=title, headline=headline, paragraphs=paragraphs, **kwargs)

    @staticmethod
    def not_found(
        title=_("core.pages.not_found.title"),
        headline=_("core.pages.not_found.headline"),
        paragraphs=[_("core.pages.not_found.p[0]")],
        **kwargs,
    ):
        """Create a new core.viewmodels.ErrorPage with defaults for a 404."""
        path = kwargs.pop("path", None)
        if path and title:
            title = f"{title}: {path}"
        elif path and not title:
            title = path
        return ErrorPage(title=title, headline=headline, paragraphs=paragraphs, **kwargs)


class PaymentProcessor:
    """
    Represents a core.models.PaymentProcessor:
    * model: core.models.PaymentProcessor
    * access_token_url: str
    * element_id: str
    * color: str
    * [name: str]
    * [loading_text: str]
    """

    def __init__(self, model, access_token_url, element_id, color, name=None, loading_text=_("core.buttons.wait")):
        if isinstance(model, models.PaymentProcessor):
            self.access_token_url = access_token_url
            self.element_id = element_id
            self.color = color
            self.name = name or model.name
            self.loading_text = loading_text
            self.card_tokenize_url = model.card_tokenize_url
            self.card_tokenize_func = model.card_tokenize_func
            self.card_tokenize_env = model.card_tokenize_env

    def context_dict(self):
        """Return a context dict for a PaymentProcessor."""
        return {"payment_processor": self}


class TransitAgency:
    """
    Represents a core.models.TransitAgency:
    * model: core.models.TransitAgency
    """

    def __init__(self, model):
        if isinstance(model, models.TransitAgency):
            self.slug = model.slug
            self.short_name = model.short_name
            self.long_name = model.long_name
            self.agency_id = model.agency_id
            self.merchant_id = model.merchant_id
            self.info_url = model.info_url
            self.phone = model.phone
            self.eligibility_index_url = model.eligibility_index_url

    def context_dict(self):
        """Return a context dict for a TransitAgency."""
        return {"agency": self}
