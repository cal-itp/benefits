"""
The core application: view model definitions for the root of the webapp.
"""
from django.utils.translation import gettext_lazy as _

from benefits.core import models


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
