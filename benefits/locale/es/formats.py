# Both “d” and “e” are backslash-escaped, because otherwise each is a format string
# that displays the day and the timezone name, respectively.
# Instead we want the literal word "de"
# https://docs.djangoproject.com/en/5.0/ref/templates/builtins/#date-and-time-formatting-specifiers
DATE_FORMAT = r"j \d\e F \d\e Y"
