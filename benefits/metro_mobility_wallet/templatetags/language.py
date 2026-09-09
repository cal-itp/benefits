from django import template

from benefits.metro_mobility_wallet.conf import LANGUAGES_METRO

register = template.Library()


@register.simple_tag
def get_metro_languages():
    """
    Store a list of Metro-app-only available languages in the context.

    Usage::

        {% get_available_languages as LANGUAGES %}
        {% for language in LANGUAGES %}
        ...
        {% endfor %}

    This puts benefits.metro_mobility_wallet.conf.LANGUAGES_METRO into the named variable.
    """
    return LANGUAGES_METRO
