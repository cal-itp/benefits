# Automated tests

## Integration

End-to-end integration tests are implemented with [`cypress`](https://www.cypress.io/) and can be found in the
[`tests/e2e`](https://github.com/cal-itp/benefits/tree/dev/tests/e2e) directory in the repository.

See the [`cypress` Command Line](https://docs.cypress.io/guides/guides/command-line) guide for more information.

### Using Docker Compose

Run the tests with Docker Compose, from inside the `localhost` directory, against the `client` service:

```bash
docker compose run tests-e2e
```

### From the Dev Container

`cypress` is installed and available to run in a terminal in the [Dev Container](development.md#vs-code-with-dev-containers).

From within the `tests/e2e` directory:

```bash
npx cypress run
```
