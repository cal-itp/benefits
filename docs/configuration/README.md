# Configuring the Benefits app

The [Getting Started][getting-started] section and sample configuration values in the repository give enough detail to
run the app locally, but further configuration is required before many of the integrations and features are active.

There are two primary components of the application configuration:

- Overall app settings in [environment variables][env-vars]
- Content and more specific configurations in [the data migration file][data]

Many (but not all) of the environment variables are read into [Django settings](#django-settings) during application
startup.

The model objects defined in the data migration file are also loaded into and seed Django's database at application startup time.

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

!!! tldr "Django docs"

    [Using settings in Python code][django-using-settings]

From within the application, the Django settings object and the Django models are the two interfaces for application code to
read configuration data.

Rather than importing the app's settings module, Django recommends importing the `django.conf.settings` object, which provides
an abstraction and better handles default values:

```python
from django.config import settings

# ...

if settings.ADMIN:
    # do something when admin is enabled
else:
    # do something else when admin is disabled
```

Through the [Django model][django-model] framework, `benefits.core.models` instances are used to access the configuration data:

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
[django-model]: https://docs.djangoproject.com/en/4.0/topics/db/models/
[django-settings]: https://docs.djangoproject.com/en/4.0/topics/settings/
[django-using-settings]: https://docs.djangoproject.com/en/4.0/topics/settings/#using-settings-in-python-code
[env-vars]: environment-variables.md
[data]: data.md
[getting-started]: ../getting-started/README.md
