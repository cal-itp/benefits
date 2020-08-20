"""
The core application: view model definitions for the root of the webapp.
"""


class Button():
    """"
    Represents a clickable button as styled <a> element:
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
        self.text = kwargs.get("text", "Button")
        self.url = kwargs.get("url")


class Icon():
    """Represents a graphical icon."""
    def __init__(self, icon, alt):
        self.icon = icon
        self.alt = alt


class Page():
    """
    Represents a page of content:
    * title: str
    * icon: core.viewmodels.Icon
    * content_title: str
    * paragraphs: str[]
    * steps: str[]
    * form: django.forms.Form
    * prev_button: core.viewmodels.Button
    * next_button: core.viewmodels.Button
    * debug: Any
    """
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.icon = kwargs.get("icon")
        self.content_title = kwargs.get("content_title")
        self.paragraphs = kwargs.get("paragraphs", [])
        self.steps = kwargs.get("steps")
        self.form = kwargs.get("form")
        self.prev_button = kwargs.get("prev_button")
        self.next_button = kwargs.get("next_button")
        self.debug = kwargs.get("debug")


def page_context(page):
    """Return a context dict for the page."""
    return {"page": page}
