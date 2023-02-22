# Automated tests

## Cypress

Feature and user interface tests are implemented with [`cypress`](https://www.cypress.io/) and can be found in the
[`tests/cypress`](https://github.com/cal-itp/benefits/tree/dev/tests/cypress) directory in the repository.

See the [`cypress` Command Line](https://docs.cypress.io/guides/guides/command-line) guide for more information.

### Running

These are instructions for running `cypress` locally on your machine, _without_ the [devcontainer](../development/README.md#vs-code-with-devcontainers). These steps
will install `cypress` and its dependencies on your machine. Make sure to run these commands in a Terminal.

1. Ensure you have Node.js and NPM available on your local machine:

```bash
node -v
npm -v
```

If not, [install Node.js](https://nodejs.org/en/download/) locally.

2. Start the the application container

```bash
cd .devcontainer/
docker compose up -d client
```

3. Change into the `cypress` directory:

```bash
cd ..
cd tests/cypress
```

4. Install all packages and `cypress`. Verify `cypress` installation succeeds:

```bash
npm install
npx cypress install
npx cypress verify
```

5. Run `cypress` with test environment variables and configuration variables:

```bash
CYPRESS_baseUrl=http://localhost:8000 npm run cypress:open
```

See `tests/cypress/package.json` for more cypress scripts.

As of Cypress 12.5.1 with Firefox 109, there is a CSRF issue that prevents the tests from passing; unclear if this is a bug in Cypress or what. Use one of the other browser options.

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

We also make the latest (from `dev`) coverage report available online here: [Coverage report](./coverage)
