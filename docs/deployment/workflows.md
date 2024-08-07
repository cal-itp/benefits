# Workflows

The GitHub Actions deployment workflow configuration lives at [`.github/workflows/deploy.yml`][deploy].

!!! info

    The entire process from GitHub commit to full redeploy of the application can take from around 5 minutes to 10 minutes
    or more depending on the deploy environment. Have patience!

## Deployment steps

The workflow is [triggered][gh-actions-trigger] with a `push` to the `main` branch or when a release candidate or release tag is created on any branch. It also responds to the `workflow_dispatch` event to allow manually triggering via the GitHub Actions UI.

When a deployment workflow runs, the following steps are taken:

### 1. Checkout code

From the tip of the corresponding branch (e.g. `main`) or the tagged commit

### 2. Authenticate to GHCR

Using the `github.actor` and built-in `GITHUB_TOKEN` secret

### 3. Build and push image to GitHub Container Registry (GHCR)

Build the root [`Dockerfile`][dockerfile], tagging with the SHA from the HEAD commit or tagged commit.

Push this image:tag into [GHCR][ghcr].

### 4. App Service deploy

Push the new image:tag to the Azure App Service instance.

[deploy]: https://github.com/cal-itp/benefits/blob/main/.github/workflows/deploy.yml
[dockerfile]: https://github.com/cal-itp/benefits/blob/main/appcontainer/Dockerfile
[ghcr]: https://github.com/features/packages
[gh-actions-trigger]: https://docs.github.com/en/actions/reference/events-that-trigger-workflows
