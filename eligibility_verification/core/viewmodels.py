"""
The core application: view model definitions for the root of the webapp.
"""


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
    * debug: Any
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
        self.debug = kwargs.get("debug")
        self.buttons = kwargs.get("buttons", [])
        if not isinstance(self.buttons, list):
            self.buttons = [self.buttons]
        if "button" in kwargs:
            self.buttons.append(kwargs.get("button"))

    def context_dict(self):
        """Return a context dict for a Page."""
        return {"page": self}


class ErrorPage(Page):
    """
    Represents an error page:
    * title: str
    * content_title: str
    * paragraphs: str[]
    * button: core.viewmodels.Button
    * debug: Any
    """
    def __init__(self, **kwargs):
        super().__init__(
            title=kwargs.get("title", "Error"),
            icon=Icon("busfail", "Bus with flat tire icon"),
            content_title=kwargs.get("content_title", "System is down"),
            paragraphs=kwargs.get("paragraphs", [
                "Unfortunately, our system is having a problem right now.",
                "Please check back later"
            ]),
            button=kwargs.get("button"),
            debug=kwargs.get("debug")
        )


BASE_PAGE = Page(
    title="Transit Discounts",
    image=Image("riderboardingbusandtapping.svg", "Senior transit rider"),
    content_title="The new way to pay for transit makes it easier to get \
        your discount every time you ride",
    paragraphs=[
        "With new contactless payment options, you can tap your payment card \
            when you board and your discount will automatically apply.",
        "Verify your discount and connect your payment card today."
    ]
)


def page_from_base(
        title=BASE_PAGE.title,
        image=BASE_PAGE.image,
        content_title=BASE_PAGE.content_title,
        paragraphs=list(BASE_PAGE.paragraphs),
        **kwargs):
    """Create a new core.viewmodels.Page instance using core.viewmodels.BASE_PAGE as defaults."""
    return Page(
        title=title,
        image=image,
        content_title=content_title,
        paragraphs=list(paragraphs),
        **kwargs
    )
