# Automated tests

## Pytest

The tests done at a request/unit level are run via [pytest-django](https://pytest-django.readthedocs.io/en/latest/index.html).

To run locally, start the [Devcontainer](../development/README.md) and run:

```bash
tests/pytest/run.sh
```

The helper script:

1. Runs the tests with `pytest`
2. Calculates test coverage with [`coverage`](https://coverage.readthedocs.io/en/latest/)
3. Generates a `coverage` report in HTML in the app's `static/` directory

The report can be viewed by launching the app and navigating to `http://localhost:$DJANGO_LOCAL_PORT/static/coverage/index.html`

The report files include a local `.gitignore` file, so the entire directory is hidden from source control.

### Latest coverage report

We also make the latest (from `main`) coverage report available online here: [Coverage report](../coverage)
