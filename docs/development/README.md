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

1. <kbd>Ctrl</kbd>/<kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> to bring up the command palette in Visual Studio Code
1. Type `Remote-Containers` to filter the commands
1. Select `Rebuild and Reopen in Container` to completely rebuild the devcontainer
1. Select `Reopen in Container` to reopen the most recent devcontainer build

## Attach a debugger

Once running inside a container, press <kbd>F5</kbd> to attach a debugger to the client, running on `http://localhost` at a port
dynamically assigned by Docker. See [Docker dynamic ports](./docker-dynamic-ports.md) for more information.

Add breakpoints in the code and browse the local site to trigger a pause. Press <kbd>F5</kbd> to continue execution from the breakpoint.

### Changing launch configuration

By default, the application is launched with `DJANGO_DEBUG=True`, causing Django to provide additional logging and error output and to relax certain security settings.

Alternatively, you may attach to an instance launched with `DJANGO_DEBUG=False`, to allow debugging the app in a state more similar to production.

In VS Code, press <kbd>Ctrl</kbd>/<kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>D</kbd> to open the `Run and Debug` pane, where you can select between the various configurations (disregard the duplicate entry, selecting either will work):

![Screenshot of the VSCode Run and Debug pane, showing selection of the launch configuration](img/vscode-debugger-launch-config.png)

The [environment](../configuration/environment-variables.md) can also be overridden for the debug session by editing the configuration in `.vscode/launch.json`, where any of the supported environment variables may be specified in the `env` block:

```json
{
    "name": "Django: Benefits Client",
    "type": "python",
    "request": "launch",
    "program": "${workspaceFolder}/manage.py",
    "args": ["runserver", "--insecure", "0.0.0.0:8000"],
    "django": true,
    "env": {
        "DJANGO_DEBUG": "true",
    }
}
```

## Exiting devcontainers

To close out of the container and re-open the directory locally in Visual Studio Code:

1. <kbd>Ctrl</kbd>/<kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> to bring up the command palette in Visual Studio Code
1. Type `Remote-Containers` to filter the commands
1. Select `Reopen Locally`

[config-file]: https://github.com/cal-itp/benefits/blob/dev/.devcontainer/devcontainer.json
[vscode]: https://code.visualstudio.com/
[vscode-containers]: https://code.visualstudio.com/docs/remote/containers
