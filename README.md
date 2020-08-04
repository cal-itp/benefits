# Eligibility Verification

Transit discount eligibility verification, minus the paperwork.

## Development

Clone the repository locally:

```bash
git clone https://github.com/cal-itp/eligibility-verification
cd eligibility-verification
```

Create an environment file from the sample:

```bash
cp .env.sample .env
```

### Recommended: VS Code with Dev Containers

[VS Code][vscode] can be used together with [Docker][docker] via the [Remote - Containers][vscode-containers] extension to use
a Docker container as a consistent development environment. This repository includes a [`.devcontainer.json`][config-file]
configuration file enabling remote container development.

First build the base image (from Python 3.8):

```bash
docker-compose build base
```

With the [Remote - Containers][vscode-containers] extension enabled, open the folder containing this repository inside Visual
Studio Code.

You should receive a prompt in the Visual Studio Code window; click `Reopen in Container` to run the development environment
inside a container.

If you do not receive a prompt:

1. `Ctrl+Shift+P` to bring up the command palette in Visual Studio Code
1. Type `Remote-Containers` to filter the commands
1. Select `Reopen in Container`

The client is running at `http://localhost:${CLIENT_LOCAL_PORT}` (http://localhost:8000 by default).

A [pgAdmin][pgadmin] container is also running at `http://localhost:${PGADMIN_LOCAL_PORT}` (http://localhost:8001 by default).
Connect using details from the `.env` file.

[config-file]: ./.devcontainer.json
[docker]: https://docs.docker.com/
[pgadmin]: https://www.pgadmin.org/
[vscode]: https://code.visualstudio.com/
[vscode-containers]: https://code.visualstudio.com/docs/remote/containers
