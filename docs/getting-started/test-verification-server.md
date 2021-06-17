# The test verification server

A basic eligibility verification server is available for testing:

```bash
docker-compose up --build server
```

The API endpoint is running at `http://localhost:5000/verify`.

From within a local `client` container, the API endpoint is at `http://server:5000/verify`
using the service-forwarding features of Docker Compose.
