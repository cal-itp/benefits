# Configuring Rate Limiting

The benefits application has a simple, single-configuration Rate Limit feature that acts per-session to limit the
number of consecutive requests in a given time period.

## Applying to Django code

The [`RateLimit` middleware][benefits-middleware] can be installed globally for all requests with the
[`MIDDLEWARE` setting][django-middleware], or per-view with a function decorator.

The latter approach is how the Benefits application rate-limits the Eligibility verification form (which is shown on the
`confirm` route/view):

```python
from django.utils.decorators import decorator_from_middleware

from benefits.core.middleware import RateLimit


@decorator_from_middleware(RateLimit)
def confirm(request):
    """View handler for the eligibility verification form."""
    # ...
```

## Environment variables

!!! warning

    The following environment variables are all required to activate the Rate Limit feature

### `DJANGO_RATE_LIMIT`

Number of requests allowed in the given [`DJANGO_RATE_LIMIT_PERIOD`](#DJANGO_RATE_LIMIT_PERIOD).

Must be greater than `0`.

### `DJANGO_RATE_LIMIT_METHODS`

Comma-separated list of HTTP Methods for which requests are rate limited.

### `DJANGO_RATE_LIMIT_PERIOD`

Number of seconds before additional requests are denied.

[benefits-middleware]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/middleware.py
[django-middleware]: https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-MIDDLEWARE
