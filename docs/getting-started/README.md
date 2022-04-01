# Local setup

Running the Benefits application in a local, non-production environment requires [Docker][docker].

The following commands should be run in a terminal program like `bash`.

## Clone the repository

```bash
git clone https://github.com/cal-itp/benefits
```

## Change into the .devcontainer dir

This is where configuration for running locally is stored.

```bash
cd benefits/.devcontainer
```

## Create an environment file

Use the sample as a template, the default values will work for now.

```bash
cp .env.sample .env
```

## Build image using Docker Compose

```bash
docker compose build --no-cache client
```

## Start the client

```bash
docker compose up [-d] client
```

The optional `-d` flag will start in _detatched_ mode and allow you to continue using the terminal session. Otherwise your
terminal will be attached to the container's terminal, showing the startup and runtime output.

After initialization, the client is running running on `http://localhost` at a port dynamically assigned by Docker. See
[Docker dynamic ports](../development/docker-dynamic-ports.md) for more information on accessing the site on localhost.

If `DJANGO_ADMIN=true`, the backend administrative interface can be accessed at the `/admin` route using the superuser account
you setup as part of initialization.

By default, [sample data][sample-data] is used to initialize Django. Alternatively you may:

* Modify the sample data file(s); or
* Point `DJANGO_INIT_PATH` at different data file(s); or
* Use production data stored in S3 (see [Deployment](../deployment)); or
* (If `DJANGO_ADMIN=true`) use the backend administrative interface CRUD

Stop the running services with:

```bash
docker compose down
```

[docker]: https://www.docker.com/products/docker-desktop
[sample-data]: https://github.com/cal-itp/benefits/tree/dev/fixtures
