# VS Code with devcontainers

!!! info

    VS Code with Devcontainers is the recommended development setup

!!! warning

    You must build the base Docker image `benefits_client:latest` before running the devcontainer.
    See [Local Setup](../getting-started/README.md)

## Install the `Remote - Containers` extension

[VS Code][vscode] can be used together with Docker via the [Remote - Containers][vscode-containers] extension to enable a
container-based development environment. This repository includes a [`.devcontainer.json`][config-file] file that configures
remote container development and debugging.

## Open the repository with VS Code

With the [Remote - Containers][vscode-containers] extension enabled, open the folder containing this repository inside Visual
Studio Code.

You should receive a prompt in the Visual Studio Code window; click `Reopen in Container` to run the development environment
inside a container.

If you do not receive a prompt, or when you feel like starting from a fresh environment:

1. `Ctrl/Cmd+Shift+P` to bring up the command palette in Visual Studio Code
1. Type `Remote-Containers` to filter the commands
1. Select `Rebuild and Reopen in Container` to completely rebuild the devcontainer
1. Select `Reopen in Container` to reopen the most recent devcontainer build

## Attach a debugger

Once running inside a container, press **`F5`** to attach a debugger to the client, running on `http://localhost` at a port
dynamically assigned by Docker. See [Docker dynamic ports](./docker-dynamic-ports.md) for more information.

Add breakpoints in the code and browse the local site to trigger a pause. Press `F5` to continue execution from the breakpoint.

## Exiting devcontainers

To close out of the container and re-open the directory locally in Visual Studio Code:

1. `Ctrl/Cmd+Shift+P` to bring up the command palette in Visual Studio Code
1. Type `Remote-Containers` to filter the commands
1. Select `Reopen Locally`

[config-file]: https://github.com/cal-itp/benefits/blob/dev/.devcontainer.json
[vscode]: https://code.visualstudio.com/
[vscode-containers]: https://code.visualstudio.com/docs/remote/containers
