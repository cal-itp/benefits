"""
The core application: view model definitions for the root of the webapp.
"""
from . import models, session


class Button():
    """"
    Represents a clickable button as styled <a> element (with optional label):
    * label: str
    * classes: str, str[]
    * text: str
    * url: str
    """
    def __init__(self, **kwargs):
        classes = kwargs.get("classes", [])
        if isinstance(classes, str):
            classes = classes.split()

        self.classes = ["btn", "btn-lg"]
        self.classes.extend(classes)
        self.label = kwargs.get("label")
        self.text = kwargs.get("text", "Button")
        self.url = kwargs.get("url")

    @staticmethod
    def agency_phone_link(agency):
        """Create a tel: link button with the agency's phone number."""
        return Button.link(
            classes="pt-0",
            label=agency.long_name,
            text=agency.phone,
            url=f"tel:{agency.phone}"
        )

    @staticmethod
    def home(request, text="Return home"):
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


def active_agency_phone_links():
    """Generate a list of core.viewmodels.Button of tel: links for each active agency."""
    return [Button.agency_phone_link(a) for a in models.TransitAgency.all_active()]


class Image():
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


class MediaItem():
    """"
    Represents a list item:
    * icon: core.viewmodels.Icon
    * heading: str
    * details: str
    """
    def __init__(self, icon, heading, details):
        self.icon = icon
        self.heading = heading
        self.details = details


class Page():
    """
    Represents a page of content:
    * title: str
    * image: core.viewmodels.Image
    * icon: core.viewmodels.Icon
    * content_title: str
    * media: core.viewmodels.MediaItem[]
    * paragraphs: str[]
    * form: django.forms.Form
    * button: core.viewmodels.Button
    * buttons: core.viewmodels.Button[]
    * classes: str[]
    """
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.image = kwargs.get("image")
        self.icon = kwargs.get("icon")
        self.content_title = kwargs.get("content_title")
        self.media = kwargs.get("media", [])
        self.paragraphs = kwargs.get("paragraphs", [])
        self.steps = kwargs.get("steps")
        self.form = kwargs.get("form")

        self.buttons = kwargs.get("buttons", [])
        if not isinstance(self.buttons, list):
            self.buttons = [self.buttons]
        if "button" in kwargs:
            self.buttons.append(kwargs.get("button"))

        self.classes = kwargs.get("classes", [])
        if not isinstance(self.classes, list):
            self.classes = self.classes.split(" ")

    def context_dict(self):
        """Return a context dict for a Page."""
        return {"page": self}

    @staticmethod
    def from_base(
            title="Transit Discounts",
            image=Image("riderboardingbusandtapping.svg", "Senior transit rider"),
            content_title="The new way to pay for transit makes it easier to get your discount every time you ride",
            paragraphs=[
                "With new contactless payment options, you can tap your payment card \
                    when you board and your discount will automatically apply.",
                "Verify your discount and connect your payment card today."
            ],
            **kwargs):
        """Create a new core.viewmodels.Page instance using sensible defaults."""
        return Page(
            title=title,
            image=image,
            content_title=content_title,
            paragraphs=list(paragraphs),
            **kwargs
        )


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
            title=kwargs.get("title", "Error"),
            icon=kwargs.get("icon", Icon("busfail", "Bus with flat tire icon")),
            content_title=kwargs.get("content_title", "Error"),
            paragraphs=kwargs.get("paragraphs", ["Unfortunately, our system is having a problem right now."]),
            button=kwargs.get("button")
        )

    @staticmethod
    def error(
            title="Service is down",
            content_title="Service is down",
            paragraphs=["We should be back in operation soon!", "Please check back later."],
            **kwargs):
        """Create a new core.viewmodels.ErrorPage instance with defaults for a generic error."""
        return ErrorPage(
            title=title,
            content_title=content_title,
            paragraphs=paragraphs,
            **kwargs
        )

    @staticmethod
    def not_found(
            title="Page not found",
            content_title="We can’t find that page",
            paragraphs=["It looks like that page doesn’t exist or it was moved."],
            **kwargs):
        """Create a new core.viewmodels.ErrorPage with defaults for a 404."""
        path = kwargs.pop("path", None)
        if path and title:
            title = f"{title}: {path}"
        elif path and not title:
            title = path
        return ErrorPage(
            title=title,
            content_title=content_title,
            paragraphs=paragraphs,
            **kwargs
        )
