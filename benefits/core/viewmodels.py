"""
The core application: view model definitions for the root of the webapp.
"""
from django.utils.translation import pgettext, ugettext as _

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
    def home(request, text=_("core.buttons.home")):
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


class Image:
    """Represents a generic image."""

    def __init__(self, src, alt):
        self.src = src
        if not self.src.startswith("http"):
            self.src = f"img/{self.src}"

        self.alt = alt


class Icon(Image):
    """Represents an icon."""

    def __init__(self, icon, alt):
        super().__init__(src=f"icon/{icon}.svg", alt=alt)


class MediaItem:
    """
    Represents a list item:
    * icon: core.viewmodels.Icon
    * heading: str
    * details: str
    """

    def __init__(self, icon, heading, details):
        self.icon = icon
        self.heading = heading
        self.details = details


class Page:
    """
    Represents a page of content:
    * title: str
    * image: core.viewmodels.Image
    * icon: core.viewmodels.Icon
    * content_title: str
    * media: core.viewmodels.MediaItem[]
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
            self.title = _("core.page.title")
        else:
            self.title = f"{_('core.page.title')}: {self.title}"

        self.image = kwargs.get("image")
        self.icon = kwargs.get("icon")
        self.content_title = kwargs.get("content_title")
        self.media = kwargs.get("media", [])
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
        if isinstance(self.image, Image):
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
            title=kwargs.get("title", _("core.error")),
            icon=kwargs.get("icon", Icon("sadbus", pgettext("image alt text", "core.icons.sadbus"))),
            content_title=kwargs.get("content_title", _("core.error")),
            paragraphs=kwargs.get("paragraphs", [_("core.error.server.content_title")]),
            button=kwargs.get("button"),
        )

    @staticmethod
    def error(
        title=_("core.error.server.title"),
        content_title=_("core.error.server.title"),
        paragraphs=[_("core.error.server.p1"), _("core.error.server.p2")],
        **kwargs,
    ):
        """Create a new core.viewmodels.ErrorPage instance with defaults for a generic error."""
        return ErrorPage(title=title, content_title=content_title, paragraphs=paragraphs, **kwargs)

    @staticmethod
    def not_found(
        title=_("core.error.notfound.title"),
        content_title=_("core.error.notfound.content_title"),
        paragraphs=[_("core.error.notfound.p1")],
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
    * access_token: str
    * element_id: str
    * color: str
    * [name: str]
    * [loading_text: str]
    """

    def __init__(self, model, access_token, element_id, color, name=None, loading_text=_("core.buttons.wait")):
        if isinstance(model, models.PaymentProcessor):
            self.access_token = access_token
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
