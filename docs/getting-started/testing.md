# Automated tests

## Integration

End-to-end integration tests are implemented with [`cypress`](https://www.cypress.io/) and can be found in the
[`tests/cypress`](https://github.com/cal-itp/benefits/tree/dev/tests/cypress) directory in the repository.

See the [`cypress` Command Line](https://docs.cypress.io/guides/guides/command-line) guide for more information.

### Running in the Dev Container

`cypress` is installed and available to run directly in the devcontainer.

1. Ensure your `.env` file has an updated `CYPRESS_baseUrl` variable:

    ```env
    # using localhost since we're inside the container
    CYPRESS_baseURL=http://localhost:8000
    ```

2. Rebuild and Reopen the devcontainer
3. Start the `benefits` app with `F5`
4. From within the `tests/cypress` directory:

    ```bash
    npx cypress run
    ```
