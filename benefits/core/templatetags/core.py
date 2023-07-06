from django import template

register = template.Library()


@register.inclusion_tag("core/tags/icon.html")
def icon(name, alt):
    """
    Defines a tag `{% icon name="" alt="" %}`
    """
    return {"name": name, "alt": alt}


@register.tag
def media_item(parser, token):
    """
    Defines the compile function for the tag `{% media_item %}{% endmedia_item %}`
    """
    # token.contents is the tag name + all arguments
    # "media_item icon='name' icon_alt='alt' heading=variable"
    # split and discard the first (tag name)
    token_contents = token.split_contents()[1:]
    args = ["icon", "icon_alt", "heading"]
    # token_contents are string "key=value" pairs, convert to dict
    kwargs = {}
    for token_arg in token_contents:
        k, v = token_arg.split("=")
        if k in args:
            kwargs[k] = v

    # parse the rest of the tag contents
    nodelist = parser.parse(("endmedia_item",))
    # "consume" the end tag
    # https://docs.djangoproject.com/en/4.2/howto/custom-template-tags/#parsing-until-another-block-tag
    parser.delete_first_token()

    return MediaItemNode(nodelist, args, **kwargs)


class MediaItemNode(template.Node):
    """
    Template Node representing an instance of a tag `{% media_item %}{% endmedia_item %}`.
    """

    def __init__(self, nodelist, arg_names, **kwargs):
        # the nodelist represents the tag inner content
        self.nodelist = nodelist
        self.arg_names = arg_names
        # create template variables for each tag argument
        for name in arg_names:
            val = kwargs.get(name)
            if val:
                setattr(self, name, template.Variable(val))

    def render(self, context):
        # render the nodelist (tag inner content) into a new "body" context
        ctx = template.Context({"body": self.nodelist.render(context)}, autoescape=context.autoescape)
        # add the tag arguments to context, .resolve() each template.Variable
        for arg in self.arg_names:
            try:
                ctx[arg] = getattr(self, arg).resolve(context)
            except AttributeError:
                pass
        # render the tag template
        t = context.template.engine.get_template("core/tags/media_item.html")
        return t.render(ctx)


@register.tag
def button(parser, token):
    """
    Defines the compile function for the tag `{% button %}{% endbutton %}`
    """
    # token.contents is the tag name + all arguments
    # "button url='/url' classes='cls' id=variable"
    # split and discard the first (tag name)
    token_contents = token.split_contents()[1:]
    # the arg keys supported by this tag
    args = ["url", "classes", "id", "target", "rel", "role"]
    # token_contents are string "key=value" pairs, convert to dict
    kwargs = {}
    for token_arg in token_contents:
        k, v = token_arg.split("=")
        if k in args:
            kwargs[k] = v

    # parse the rest of the tag contents
    nodelist = parser.parse(("endbutton",))
    # "consume" the end tag
    # https://docs.djangoproject.com/en/4.2/howto/custom-template-tags/#parsing-until-another-block-tag
    parser.delete_first_token()
    return ButtonNodeItem(nodelist, args, **kwargs)


class ButtonNodeItem(template.Node):
    """
    Template Node representing an instance of a tag `{% button url="" classes="" %}{% endbutton %}`.
    """

    def __init__(self, nodelist, arg_names, **kwargs):
        self.nodelist = nodelist
        self.arg_names = arg_names
        for name in arg_names:
            val = kwargs.get(name)
            if val:
                setattr(self, name, template.Variable(val))

    def render(self, context):
        # render the nodelist (tag inner content) into a new "body" context
        ctx = template.Context({"body": self.nodelist.render(context)}, autoescape=context.autoescape)
        # add the tag arguments to context, .resolve() each template.Variable
        for arg in self.arg_names:
            try:
                ctx[arg] = getattr(self, arg).resolve(context)
            except AttributeError:
                pass
        # adjust classes to list as-needed
        classes = ctx.get("classes")
        if isinstance(classes, str):
            ctx["classes"] = classes.split(" ")
        # render the tag template
        t = context.template.engine.get_template("core/tags/button.html")
        return t.render(ctx)


@register.inclusion_tag("core/tags/button__previous_page.html")
def button__previous_page(url):
    """
    Defines a tag `{% button__previous_page url="" %}`
    """
    return {"url": url}
