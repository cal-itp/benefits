from django import template

register = template.Library()


@register.inclusion_tag("core/tags/icon.html")
def icon(name, alt):
    """
    Defines a tag `{% icon name="" alt="" %}`
    """
    return {"name": name, "alt": alt}
