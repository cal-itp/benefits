# Development

This repository uses [`pre-commit`][pre-commit] hooks to check and format code.

Ensure you have `pre-commit` installed:

```console
pip install pre-commit
```

Then run (from the root of this repository):

```console
bin/pre-commit.sh
```

### VS Code with Dev Containers

**This is the recommended development setup**.

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

### Attach a debugger

Once running inside a container, press **`F5`** to attach a debugger to the client at `http://localhost:${DJANGO_LOCAL_PORT}`
(<http://localhost:8000> by default) on your host machine.

Add breakpoints in the code and browse the local site to trigger them.

### Test verification server

The [test eligibility verification server](./test-verification-server.md) endpoint is running at `http://localhost:5000/verify`
on your host machine. Access the server endpoint from within the Dev Container at `http://server:5000/verify`.

### Exiting dev containers

To close out of the container and re-open the directory locally in Visual Studio Code:

1. `Ctrl+Shift+P` to bring up the command palette in Visual Studio Code
1. Type `Remote-Containers` to filter the commands
1. Select `Reopen Locally`

[config-file]: https://github.com/cal-itp/benefits/blob/dev/.devcontainer.json
[pre-commit]: https://pre-commit.com/
[vscode]: https://code.visualstudio.com/
[vscode-containers]: https://code.visualstudio.com/docs/remote/containers
