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

If you are running `bash`, shortcut the following steps with the [`setup`](./setup) script:

```bash
./setup
```

Otherwise, start by building the eligibility verification client image:

```bash
docker-compose build --no-cache client
```

Run Django database migrations:

```bash
docker-compose run client migrate
```

Load [sample Django model data](./data/client):

```bash
docker-compose run client data
```

Create a superuser account for Django backend admin access (follow the CLI prompts):

```bash
docker-compose run client superuser
```

### Run the client locally

```bash
docker-compose up -d client
```

The client is running at `http://localhost:${DJANGO_LOCAL_PORT}` (<http://localhost:8000> by default).

The backend administrative interface can be accessed with the superuser you setup at <http://localhost:8000/admin>.

Stop a running client (and supporting containers) with:

```bash
docker-compose down
```

### Run a local test verification server

A basic eligibility verification server is available for testing:

```bash
docker-compose up -d --build server
```

The API endpoint is running at `http://localhost:5000/verify`.

Sample users and eligiblity can be found in [`data/server/db.json`](./data/server/db.json).

## VS Code with Dev Containers

[VS Code][vscode] can be used together with Docker via the [Remote - Containers][vscode-containers] extension to enable a
container-based development environment. This repository includes a [`.devcontainer.json`][config-file] file that configures
remote container development and debugging.

With the [Remote - Containers][vscode-containers] extension enabled, open the folder containing this repository inside Visual
Studio Code.

You should receive a prompt in the Visual Studio Code window; click `Reopen in Container` to run the development environment
inside a container.

If you do not receive a prompt, or when you feel like starting from a fresh environment:

1. `Ctrl+Shift+P` to bring up the command palette in Visual Studio Code
1. Type `Remote-Containers` to filter the commands
1. Select `Rebuild and Reopen in Container`

Once running inside a container, press **`F5`** to attach a debugger to the client at `http://localhost:${DJANGO_LOCAL_PORT}`
(<http://localhost:8000> by default) on your host machine.

The test eligibility verification server endpoint is running at `http://localhost:5000/verify` on your host machine.
Access the server endpoint from within the Dev Container at `http://server:5000/verify`.

To close out of the container and re-open the directory locally in Visual Studio Code:

1. `Ctrl+Shift+P` to bring up the command palette in Visual Studio Code
1. Type `Remote-Containers` to filter the commands
1. Select `Reopen Locally`

[config-file]: ./.devcontainer.json
[docker]: https://docs.docker.com/
[docker-compose]: https://docs.docker.com/compose/
[vscode]: https://code.visualstudio.com/
[vscode-containers]: https://code.visualstudio.com/docs/remote/containers
