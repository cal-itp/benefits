# The test verification server

A basic eligibility verification server is available for testing:

```bash
docker compose up [-d] server
```

The optional `-d` flag will start in _detatched_ mode and allow you to continue using the terminal session. Otherwise your
terminal will be attached to the container's terminal, showing the startup and runtime output.

The API server is running on `http://localhost` at a port dynamically assigned by Docker. To find the exact address, look in
the Docker Desktop UI or run the following command:

```bash
docker ps -f name=server
```

The `PORTS` column should look like:

```console
0.0.0.0:$LOCAL_PORT->5000/tcp, 0.0.0.0:$DEBUG_PORT->5678/tcp
```

Where `$LOCAL_PORT` and `$DEBUG_PORT` are the dynamically assigned `localhost` ports.

From within another Compose service container, the API is at `http://server:5000` using the service-forwarding features of
Compose.

In either case, the endpoint `/verify` serves as the Eligibility Verification API endpoint.
