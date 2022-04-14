# Configuring the Benefits app

The [Getting Started][getting-started] section and sample configuration in the repository gives enough detail to
run the app locally. But further configuration is required before many of the integrations and features are active.

There are two primary components of the application configuration include:

* Overall app settings in [environment variables][env-vars]
* Content and more specific configurations in [fixtures][fixtures]

The majority (but not all) of the environment variables are read into [Django settings](#django-settings) during application
startup.

The fixtures are also loaded into and seed Django's database at application startup time.

## Django settings

!!! example "Settings file"

    [`benefits/settings.py`][benefits-settings]

!!! tldr "Django docs"

    [Django settings][django-settings]

The Django entrypoint for production runs is defined in [`benefits/wsgi.py`][benefits-wsgi].

This file names the module that tells Django which settings file to use:

```python
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "benefits.settings")
```

Elsewhere, e.g. in [`manage.py`][benefits-manage], this same environment variable is set to ensure `benefits.settings`
are loaded for every app command and run.

## Using configuration in app code

From within the application, the Django settings file and the Django models are the two interfaces for application code to
read configuration data.

The settings file defines a number of "constants" (they aren't strictly _constant_, but should be treated as such) that
can be imported directly by application code, for example:

```python
from benefits.settings import ADMIN

# ...

if ADMIN:
    # do something when admin is enabled
else:
    # do something else when admin is disabled
```

Through the [Django model][django-model] framework, `benefits.core.models` instances are used to access the fixture data:

```python
from benefits.core.models import TransitAgency

agency = TransitAgency.objects.get(short_name="ABC")

if agency.active:
    # do something when this agency is active
else:
    # do something when this agency is inactive
```

[benefits-manage]: https://github.com/cal-itp/benefits/blob/dev/manage.py
[benefits-settings]: https://github.com/cal-itp/benefits/blob/dev/benefits/settings.py
[benefits-wsgi]: https://github.com/cal-itp/benefits/blob/dev/benefits/wsgi.py
[django-model]: https://docs.djangoproject.com/en/3.2/topics/db/models/
[django-settings]: https://docs.djangoproject.com/en/3.2/topics/settings/
[env-vars]: environment-variables.md
[fixtures]: fixtures.md
[getting-started]: ../getting-started/README.md
