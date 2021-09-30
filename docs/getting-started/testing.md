# Automated tests

## Integration

End-to-end integration tests are implemented with [`cypress`](https://www.cypress.io/) and can be found in the
[`tests/e2e`](https://github.com/cal-itp/benefits/tree/dev/tests/e2e) directory in the repository.

Run the tests with Docker Compose, from inside the `localhost` directory:

```bash
docker compose run tests-e2e
```
