from django import template


register = template.Library()


@register.inclusion_tag("eligibility/tags/media_item__start__bankcardcheck.html")
def media_item__start__bankcardcheck():
    return {}
