# Getting started

Running the Benefits application in a local, non-production environment.

Requires [Docker](https://docs.docker.com/). The following commands should be run in a terminal program like `bash`.

## Clone the repository

```bash
git clone https://github.com/cal-itp/benefits
cd benefits/localhost
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
docker compose up client
```

After initialization, the client is running at `http://localhost:${DJANGO_LOCAL_PORT}`
(<http://localhost:8000> by default).

If `DJANGO_ADMIN=true`, the backend administrative interface can be accessed with the superuser you setup at
<http://localhost:8000/admin>.

By default, [sample data][sample-data] is used to initialize Django. Alternatively you may:

* Modify the sample data file; or
* Point `DJANGO_INIT_PATH` at a different data file; or
* Use production data stored in S3 (see [Deployment](../deployment)); or
* (If `DJANGO_ADMIN=true`) use the backend administrative interface CRUD

Stop the running services with:

```bash
docker-compose down
```

[sample-data]: https://github.com/cal-itp/benefits/blob/dev/localhost/data/client.json
