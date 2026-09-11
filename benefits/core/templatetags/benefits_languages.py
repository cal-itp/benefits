from django import template

register = template.Library()


@register.simple_tag
def get_benefits_languages():
    """
    Follows Django's i18n get_available_languages
    https://github.com/django/django/blob/2b30f6255b5ef84afbd827993643d52ef2c0963a/django/templatetags/i18n.py#L219
    Store a list of Benefits-app-only available languages in the context.

    Usage::

        {% get_benefits_languages as LANGUAGES %}
        {% for language in LANGUAGES %}
        ...
        {% endfor %}

    This puts English and Spanish only into the named variable.
    """
    return [("en", "English"), ("es", "Español")]
