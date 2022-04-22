# Automated tests

## Cypress

Feature and user interface tests are implemented with [`cypress`](https://www.cypress.io/) and can be found in the
[`tests/cypress`](https://github.com/cal-itp/benefits/tree/dev/tests/cypress) directory in the repository.

See the [`cypress` Command Line](https://docs.cypress.io/guides/guides/command-line) guide for more information.

### Running in the Dev Container

`cypress` is installed and available to run directly in the [devcontainer](../development/README.md#vs-code-with-devcontainers).

1. Ensure your `.env` file has an updated `CYPRESS_baseUrl` variable:

    ```env
    # using localhost since we're inside the container
    CYPRESS_baseURL=http://localhost:8000
    ```

2. Rebuild and Reopen the devcontainer
3. Start the `benefits` app with `F5`
4. From within the `tests/cypress` directory:

    ```bash
    npm run cypress:ui
    ```

### Running outside of the Dev Container

These are instructions for running `cypress` locally on your machine, *without* the devcontainer. These steps
will install `cypress` and its dependencies on your  machine. Make sure to run these commands in a Terminal.

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

## Pytest

The tests done at a request/unit level are run via [pytest-django](https://pytest-django.readthedocs.io/en/latest/index.html). To run locally, start the [Devcontainer](../development/README.md) and run:

```bash
pytest --cov=benefits
```
