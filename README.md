# Eligibility Verification

Transit discount eligibility verification, minus the paperwork.

## Development

Requires [Docker][docker] and [Docker Compose][docker-compose].

Clone the repository locally:

```bash
git clone https://github.com/cal-itp/eligibility-verification
cd eligibility-verification
```

Create an environment file from the sample:

```bash
cp .env.sample .env
```

### Local Django setup

If you're in `bash`, shortcut the following setup steps by running:

```bash
./bin/setup.sh
```

Otherwise, start by building the eligibility verification client image:

```bash
docker-compose build --no-cache client
```

Ensure the local database container is running:

```bash
docker-compose up -d db
```

Run Django database migrations:

```bash
docker-compose run client python manage.py migrate
```

Load sample Django model data:

```bash
docker-compose run client python manage.py loaddata \
    EligibilityTypes \
    EligibilityVerifiers \
    TransitAgencies
```

Create a superuser account for Django backend admin access (follow the CLI prompts):

```bash
docker-compose run client python manage.py createsuperuser
```

### Run the client locally

```bash
docker-compose up -d client
```

The client is running at `http://localhost:${DJANGO_LOCAL_PORT}` (http://localhost:8000 by default).

### Run a local test verification server

A basic eligibility verification server is available for testing:

```bash
docker-compose up -d --build server
```

The API endpoint is running at `http://localhost:5000/verify`.

### VS Code with Dev Containers

[VS Code][vscode] can be used together with Docker via the [Remote - Containers][vscode-containers] extension to enable a
container-based development environment. This repository includes a [`.devcontainer.json`][config-file] file that configures
remote container development and debugging.

With the [Remote - Containers][vscode-containers] extension enabled, open the folder containing this repository inside Visual
Studio Code.

You should receive a prompt in the Visual Studio Code window; click `Reopen in Container` to run the development environment
inside a container.

If you do not receive a prompt:

1. `Ctrl+Shift+P` to bring up the command palette in Visual Studio Code
1. Type `Remote-Containers` to filter the commands
1. Select `Reopen in Container`

Once running inside a container, press `F5` to attach a debugger to the client at `http://localhost:${DJANGO_LOCAL_PORT}`
(http://localhost:8000 by default) on your host machine.

The test eligibility verification server container is running at `http://localhost:5000/verify` on your host machine.
Access the server from within the Dev Container at `http://server:5000/verify`.

A [pgAdmin][pgadmin] container is also running at `http://localhost:8001` on the host machine.

[config-file]: ./.devcontainer.json
[docker]: https://docs.docker.com/
[docker-compose]: https://docs.docker.com/compose/
[pgadmin]: https://www.pgadmin.org/
[vscode]: https://code.visualstudio.com/
[vscode-containers]: https://code.visualstudio.com/docs/remote/containers
