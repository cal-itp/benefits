# Test Eligibility Verification server

A basic eligibility verification server is available for testing. The server code is available on [GitHub](https://github.com/cal-itp/eligibility-server/), with its own set of [documentation](https://docs.calitp.org/eligibility-server/).

## Running locally

```bash
docker compose up [-d] server
```

The optional `-d` flag will start in _detatched_ mode and allow you to continue using the terminal session. Otherwise your
terminal will be attached to the container's terminal, showing the startup and runtime output.

The API server is running on `http://localhost` at a port dynamically assigned by Docker. See
[Docker dynamic ports](./docker-dynamic-ports.md) for more information on accessing the server on localhost.

From within another Compose service container, the server is at `http://server:5000` using the service-forwarding features of
Compose.

In either case, the endpoint `/verify` serves as the Eligibility Verification API endpoint.

## In the Devcontainer

When running the [Devcontainer](#vs-code-with-devcontainers), the server is automatically started.

See [Docker dynamic ports](./docker-dynamic-ports.md) for more information on accessing the server on localhost.

The server is accessible from within the Devcontainer at its Compose service address: `http://server:5000`.
