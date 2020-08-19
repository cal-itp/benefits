"""
The core application: view model definitions for the root of the webapp.
"""


class Button():
    """Represents a clickable button as styled <a> element."""
    def __init__(self, **kwargs):
        classes = kwargs.get("classes", [])
        if isinstance(classes, str):
            classes = classes.split()

        self.classes = ["btn", "btn-lg"]
        self.classes.extend(classes)
        self.text = kwargs.get("text", "Button")
        self.url = kwargs.get("url")


class Page():
    """
    Represents a page of content:
    * title
    * icon
    * content_title
    * paragraphs
    * form
    * prev_button
    * next_button
    * debug
    """
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.icon = kwargs.get("icon")
        self.content_title = kwargs.get("content_title")
        self.icon_alt = kwargs.get("icon_alt", f"Icon for page: '{self.title}'")
        self.paragraphs = kwargs.get("paragraphs", [])
        self.form = kwargs.get("form")
        self.prev_button = kwargs.get("prev_button")
        self.next_button = kwargs.get("next_button")
        self.debug = kwargs.get("debug")


def page_context(page):
    """Return a context dict for the page."""
    return {"page": page}
