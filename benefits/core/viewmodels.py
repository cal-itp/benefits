"""
The core application: view model definitions for the root of the webapp.
"""
from django.utils.translation import pgettext, gettext as _

from benefits.core import models

from . import session


class Button:
    """
    Represents a clickable button as styled <a> element (with optional label):
    * label: str
    * id: str
    * classes: str, str[]
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
            # fmt: off
            Button.link(classes="agency-url", label=agency.long_name, text=agency.info_url, url=agency.info_url, target="_blank", rel="noopener noreferrer"),  # noqa: E501
            Button.link(classes="agency-phone", text=agency.phone, url=f"tel:{agency.phone}"),
            # fmt: on
        ]

    @staticmethod
    def home(request, text=_("core.buttons.return_home")):
        """Create a button back to this session's origin."""
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
        btn = Button.primary(**kwargs)
        btn.classes.insert(0, "btn-login")
        return btn


class Icon:
    """Represents an icon."""

    def __init__(self, icon, alt):
        self.src = f"img/icon/{icon}.svg"
        self.alt = alt


class Page:
    """
    Represents a page of content:
    * title: str
    * noimage: bool
    * icon: core.viewmodels.Icon
    * content_title: str
    * paragraphs: str[]
    * form: django.forms.Form
    * forms: django.forms.Form[]
    * button: core.viewmodels.Button
    * buttons: core.viewmodels.Button[]
    * classes: str[]
    """

    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        if self.title is None:
            self.title = _("core.pages.index.title")
        else:
            self.title = f"{_('core.pages.index.title')}: {self.title}"

        self.noimage = kwargs.get("noimage", False)
        self.icon = kwargs.get("icon")
        self.content_title = kwargs.get("content_title")
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

        self.classes = kwargs.get("classes", [])
        if not isinstance(self.classes, list):
            self.classes = self.classes.split(" ")
        if not self.noimage:
            self.image = "img/ridertappingbankcard.png"
            self.classes.append("with-image")

    def context_dict(self):
        """Return a context dict for a Page."""
        return {"page": self}


class ErrorPage(Page):
    """
    Represents an error page:
    * title: str
    * icon: core.viewmodels.Icon
    * content_title: str
    * paragraphs: str[]
    * button: core.viewmodels.Button
    """

    def __init__(self, **kwargs):
        super().__init__(
            title=kwargs.get("title", _("core.pages.error.title")),
            icon=kwargs.get("icon", Icon("sadbus", pgettext("image alt text", "core.icons.sadbus"))),
            content_title=kwargs.get("content_title", _("core.pages.error.title")),
            paragraphs=kwargs.get("paragraphs", [_("core.pages.server_error.content_title")]),
            button=kwargs.get("button"),
        )

    @staticmethod
    def error(
        title=_("core.pages.server_error.title"),
        content_title=_("core.pages.server_error.title"),
        paragraphs=[_("core.pages.server_error.p[0]"), _("core.pages.server_error.p[1]")],
        **kwargs,
    ):
        """Create a new core.viewmodels.ErrorPage instance with defaults for a generic error."""
        return ErrorPage(title=title, content_title=content_title, paragraphs=paragraphs, **kwargs)

    @staticmethod
    def not_found(
        title=_("core.pages.not_found.title"),
        content_title=_("core.pages.not_found.content_title"),
        paragraphs=[_("core.pages.not_found.p[0]")],
        **kwargs,
    ):
        """Create a new core.viewmodels.ErrorPage with defaults for a 404."""
        path = kwargs.pop("path", None)
        if path and title:
            title = f"{title}: {path}"
        elif path and not title:
            title = path
        return ErrorPage(title=title, content_title=content_title, paragraphs=paragraphs, **kwargs)


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

    def context_dict(self):
        """Return a context dict for a TransitAgency."""
        return {"agency": self}
