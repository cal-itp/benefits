# Django models

Cal-ITP Benefits defines a number of [models][core-models] in the core application, used throughout the codebase to configure
different parts of the UI and logic. These are currently split into three files: `common.py` (for utilities and the `PemData` model), `enrollment.py` (models related to the enrollment process), and `transit.py` (models related to transit providers and processors).

Additionally, there are some models in the [`enrollment_littlepay`][littlepay-models]
and [`enrollment_switchio`][switchio-models] apps for their individual subclasses
of the base `EnrollmentGroup` and `TransitProcessorConfig` models.

The Cal-ITP Benefits database mostly acts as a read-only configuration store.
Runtime configuration changes can be persisted via [Django's Admin interface](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/).

## Updating models

When models are updated, **migrations** will need to be added and **fixtures** will need to be updated.

[Read our guide to migrations and fixtures](../guides/migrations-and-fixtures)

[core-models]: https://github.com/cal-itp/benefits/tree/main/benefits/core/models/
[littlepay-models]: https://github.com/cal-itp/benefits/blob/main/benefits/enrollment_littlepay/models.py
[switchio-models]: https://github.com/cal-itp/benefits/blob/main/benefits/enrollment_switchio/models.py
