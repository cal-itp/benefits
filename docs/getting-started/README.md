# Local setup

Running the Benefits application in a local, non-production environment requires [Docker][docker].

The following commands should be run in a terminal program like `bash`.

## Clone the repository

```bash
git clone https://github.com/cal-itp/benefits
```

## Create an environment file

The application is configured with defaults to run locally, but an `.env` file is required to run with Docker Compose. Start from the existing sample:

```bash
cp .env.sample .env
```

E.g. to change the localhost port from the default `8000` to `9000`, add the following line to your `.env` file:

```env
DJANGO_LOCAL_PORT=9000
```

!!! note

    You will need to change `DJANGO_LOCAL_PORT` to a specific value in order to test locally with the CDT Identity Gateway's dev environment. Compiler developers, this value can be found in our shared notes in LastPass.

See [Configuration](../configuration) for more details on supported environment variables and their settings.

## Run the build script

This builds the runtime and devcontainer images:

```bash
bin/build.sh
```

If you need all layers to rebuild, use:

```bash
docker compose build --no-cache client
```

## Start the client in a VS Code dev container

From this point forward, the recommended local development setup is to run the app with the [VS Code Dev Containers extension](devcontainers).

See [Devlopment](../development/) for more details on setting up a dev container and developing with it.

Alternatively, read on to run the app traditionally with Docker Compose.

## Start the client traditionally

The optional `-d` flag will start in _detatched_ mode and allow you to continue using the terminal session.

```bash
docker compose up -d client
```

Otherwise attach your terminal to the container's terminal, showing the startup and runtime output:

```bash
docker compose up client
```

After initialization, the client is running on <http://localhost:8000> by default.

The backend administrative interface can be accessed at the `/admin` route using the superuser account credentials set in your `.env` file.

Stop the running services with:

```bash
docker compose down
```

## Minimum configuration needed for your first manual end-to-end test

The following updates must be made to run a full end-to-end test using the sample agenct (CST), the Older Americans flow via Login.gov and the CDT Identity Gateway(IdG) dev environment, and the Littlepay QA environment.

!!! note

    Compiler developers, these values can be found in our shared notes in LastPass.

### `.env` updates

- Change `cst_transit_processor_client_secret` from the default (`secret`) to the appropriate value
- Set `DJANGO_LOCAL_PORT` to the right value for the dev IdG to let you connect via localhost
- Set `littlepay_qa_api_base_url`

!!! warning

    Be sure to rebuild your devcontainer beefore proceeding.

### Django Admin updates

- Identity gateway configs (benefits-logingov):
  - client_id
  - authority
- Littlepay configs ((QA) cst)
  - audience
  - client_id
- Littlepay groups (Older Adult (cst)):
  - group_id

Compiler developers, instead of setting these manually, you can:

1. Grab the "Benefits fixtures with secrets for local development" note from our shared notes in LastPass
1. Put it in a new JSON file named something like `dev_fixtures.json`
1. Change the value of `DJANGO_DB_FIXTURES` in your `.env` file to point to your new `dev_fixtures.json`
1. Rebuild the devcontainer

### Login.gov test account

For details on creating an identity-proofed account for testing in the Login.gov sandbox, see [Manual Tests](../tests/manual-tests/#getting-started-using-test-credentials).

---

You should now be ready to perform a complete end-to-end test in your local environment! When arriving at the Littlepay form, use any of the acceptable forms of [test data for Visa or MasterCard accounts](test-cards).

## Managing test data going forward

If you're going to be using the local environment you just set up for ongoing development, be aware that by default the **database will be dropped and fixtures will be reloaded every time the devcontainer is started** (not only on rebuilding). This helps ensure consistent test data across PR reviews.

Compiler developers, be sure to follow the instructions in the [Django Admin updates](#django-admin-updates) section above to set up the fixtures with our development secrets in them.

If you have a need to maintain some test data that you've added via the Django Admin across multiple development sessions:

1. Set `DJANGO_DB_RESET=false` in your `.env` file
1. Create a new set of temporary fixtures:
   ```bash
   python manage.py dumpdata --indent 2 --output benefits/core/migrations/temp_fixtures.json
   ```
   - It's important that the filename end in `fixtures.json` so that it's ignored by Git.
1. Set `DJANGO_DB_FIXTURES` to the path of the new file you just created in `.env`
1. Rebuild the devcontainer

Or, if you made a temporary change to one of the objects created by the fixtures that you don't want to lose, you can prevent the fixtures from being reloaded by setting `DJANGO_DB_FIXTURES` to `false` (or any string that doesn't resolve to a real fixtures file ending in `fixtures.json`).

[docker]: https://www.docker.com/products/docker-desktop
[devcontainers]: https://code.visualstudio.com/docs/devcontainers/containers
[data-migration]: https://github.com/cal-itp/benefits/tree/main/benefits/core/migrations
[logingov-internal]: https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit?tab=t.0#heading=h.bvwe1dyv15c5
[logingov-external]: https://developers.login.gov/testing/#testing-identity-proofing
[test-cards]: https://docs.stripe.com/testing?testing-method=card-numbers#cards
