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

The application is configured with defaults to run locally, but an `.env` file is required to run with Docker Compose. This file can be empty, or environment overrides can be added as needed:

```bash
touch .env
```

E.g. to change the localhost port from the default `8000` to `9000`, add the following line to your `.env` file:

```env
DJANGO_LOCAL_PORT=9000
```

See [Configuration](../configuration) for more details on supported environment variables and their settings.

## Build image using Docker Compose

```bash
docker compose build client
```

If you need all layers to rebuild, use:

```bash
docker compose build --no-cache client
```

## Start the client

The optional `-d` flag will start in _detatched_ mode and allow you to continue using the terminal session.

```bash
docker compose up -d client
```

Otherwise attach your terminal to the container's terminal, showing the startup and runtime output:

```bash
docker compose up client
```

After initialization, the client is running running on `http://localhost:8000` by default.

If `DJANGO_ADMIN=true`, the backend administrative interface can be accessed at the `/admin` route using the superuser account
you setup as part of initialization.

By default, [sample data][sample-data] is used to initialize Django. Alternatively you may:

* Modify the sample data file(s); or
* Override the `DJANGO_INIT_PATH` environment variable with different data file(s); or
* (If `DJANGO_ADMIN=true`) use the backend administrative interface CRUD

Stop the running services with:

```bash
docker compose down
```

[docker]: https://www.docker.com/products/docker-desktop
[sample-data]: https://github.com/cal-itp/benefits/tree/dev/fixtures
