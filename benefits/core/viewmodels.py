"""
The core application: view model definitions for the root of the webapp.
"""


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
