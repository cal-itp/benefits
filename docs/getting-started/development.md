# Development

## Branches and merging

The default GitHub branch is `dev`. All new feature work should be in the form of Pull Requests (PR) that target `dev` as their
base.

In addition to `dev`, the repository has three other long-lived branches:

* `test` and `prod` correspond to the Test and Production [deploy environments](../deployment/README.md), respectively.
* `gh-pages` hosts the compiled documentation, and is always forced-pushed by the
[docs build process](./documentation.md#deploying).

[Branch protection rules][gh-branch-protection] are in place on three environment branches (`dev`, `test`, `prod`) to:

* Prevent branch deletion
* Restrict force-pushing, where appropriate
* Require passing status checks before merging into the target branch is allowed

Merging of PRs should be done using the *merge commit* strategy. The *squash* strategy is also enabled for particularly wild or
messy PRs, but this should only be used as a last resort when it is not possible or too difficult to rebase the PR branch onto
the target branch before merging.

When merging a PR into `dev`, it is customary to format the merge commit message like:

```console
Title of PR (#number)
```

instead of the default:

```console
Merge pull request #number from source-repo/source-branch
```

Application deployments occur automatically when a PR is merged to the target environment branch. A successful deploy to
`dev` is required before a deploy to `test` is allowed; a successful deploy to `test` is required before a deploy to `prod` is
allowed.

See [Deployment](../deployment/README.md) for more information.

## pre-commit

This repository uses [`pre-commit`][pre-commit] hooks to check and format code.

Ensure you have `pre-commit` installed locally before making any commits:

```console
pip install pre-commit
```

Then run (from the root of this repository):

```console
bin/pre-commit.sh
```

Branch protection rules on the environment branches in GitHub ensure that `pre-commit` checks have passed before a merge is
allowed.

## VS Code with Devcontainers

!!! tip

    This is the recommended development setup

!!! warning

    You must build the base Docker image `benefits_client:latest` before running the devcontainer.
    See [Local Setup](./README.md)

[VS Code][vscode] can be used together with Docker via the [Remote - Containers][vscode-containers] extension to enable a
container-based development environment. This repository includes a [`.devcontainer.json`][config-file] file that configures
remote container development and debugging.

With the [Remote - Containers][vscode-containers] extension enabled, open the folder containing this repository inside Visual
Studio Code.

You should receive a prompt in the Visual Studio Code window; click `Reopen in Container` to run the development environment
inside a container.

If you do not receive a prompt, or when you feel like starting from a fresh environment:

1. `Ctrl/Cmd+Shift+P` to bring up the command palette in Visual Studio Code
1. Type `Remote-Containers` to filter the commands
1. Select `Rebuild and Reopen in Container`

### Attach a debugger

Once running inside a container, press **`F5`** to attach a debugger to the client, running on `http://localhost` at a port
dynamically assigned by Docker. See [Docker dynamic ports](./docker-dynamic-ports.md) for more information.

Add breakpoints in the code and browse the local site to trigger a pause. Press `F5` to continue execution from the breakpoint.

### Exiting devcontainers

To close out of the container and re-open the directory locally in Visual Studio Code:

1. `Ctrl/Cmd+Shift+P` to bring up the command palette in Visual Studio Code
1. Type `Remote-Containers` to filter the commands
1. Select `Reopen Locally`

## Test Eligibility Verification server

A basic eligibility verification server is available for testing. The server code is available on [GitHub](https://github.com/cal-itp/eligibility-server/), with its own set of [documentation](https://docs.calitp.org/eligibility-server/).

### Running locally

```bash
docker compose up [-d] server
```

The optional `-d` flag will start in _detatched_ mode and allow you to continue using the terminal session. Otherwise your
terminal will be attached to the container's terminal, showing the startup and runtime output.

The API server is running on `http://localhost` at a port dynamically assigned by Docker. See
[Docker dynamic ports](./docker-dynamic-ports.md) for more information on accessing the server on localhost.

From within another Compose service container, the server is at `http://server:5000` using the service-forwarding features of
Compose.

In either case, the endpoint `/verify` serves as the Eligibility Verification API endpoint.

### In the Devcontainer

When running the [Devcontainer](./development.md#vs-code-with-devcontainers), the server is automatically started.

See [Docker dynamic ports](./docker-dynamic-ports.md) for more information on accessing the server on localhost.

The server is accessible from within the Devcontainer at its Compose service address: `http://server:5000`.


[config-file]: https://github.com/cal-itp/benefits/blob/dev/.devcontainer.json
[gh-branch-protection]: https://docs.github.com/en/github/administering-a-repository/defining-the-mergeability-of-pull-requests/about-protected-branches
[pre-commit]: https://pre-commit.com/
[vscode]: https://code.visualstudio.com/
[vscode-containers]: https://code.visualstudio.com/docs/remote/containers
