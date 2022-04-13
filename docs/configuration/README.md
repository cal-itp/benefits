# Configuring the app

The [Getting Started][getting-started] section and sample configuration in the repository gives enough detail to
run the app locally. But the application requires further configuration before many of the integrations and features are active.

There are two primary components of the application configuration:

* Overall app settings in [environment variables][env-vars]
* Content and more specific configurations in [fixtures][fixtures]

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

The settings file defines a number of "constants" (they aren't strictly **constant**, but should be treated that way) that
can be imported directly by application code, for example:

```python
from benefits.settings import ADMIN

# ...

if ADMIN:
    # do something when admin is enabled
else:
    # do something else when admin is disabled
```

And model instances are used e.g. to interact with the Eligibility API:

```python
from benefits.core import models

verifier = models.EligibilityVerifier.objects.get(id=1)

requests.get(verifier.api_url)
```

[benefits-manage]: https://github.com/cal-itp/benefits/blob/dev/manage.py
[benefits-settings]: https://github.com/cal-itp/benefits/blob/dev/benefits/settings.py
[benefits-wsgi]: https://github.com/cal-itp/benefits/blob/dev/benefits/wsgi.py
[django-settings]: https://docs.djangoproject.com/en/3.2/topics/settings/
[env-vars]: environment-variables.md
[fixtures]: fixtures.md
[getting-started]: ../getting-started/README.md
