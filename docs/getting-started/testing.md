# Automated tests

## Integration

End-to-end integration tests are implemented with [`cypress`](https://www.cypress.io/) and can be found in the
[`tests/e2e`](https://github.com/cal-itp/benefits/tree/dev/tests/e2e) directory in the repository.

See the [`cypress` Command Line](https://docs.cypress.io/guides/guides/command-line) guide for more information.

### Using Docker Compose

Run the tests with Docker Compose against the `client` service.

1. Ensure your `.env` file has an updated `CYPRESS_baseUrl` variable:

    ```env
    # using the Docker Compose service address
    CYPRESS_baseURL=http://client:8000
    ```

2. From within the `localhost` directory:

    ```bash
    docker compose run tests-e2e
    ```

### From the Dev Container

`cypress` is installed and available to run directly in the devcontainer.

1. Ensure your `.env` file has an updated `CYPRESS_baseUrl` variable:

    ```env
    # using localhost since we're inside the container
    CYPRESS_baseURL=http://localhost:8000
    ```

2. Rebuild and Reopen the devcontainer
3. Start the `benefits` app with `F5`
4. From within the `tests/e2e` directory:

    ```bash
    npx cypress run
    ```
