# Workflows

The GitHub Actions deployment workflow configuration lives at [`.github/workflows/deploy.yml`][deploy].

!!! info

    The entire process from GitHub commit to full redeploy of the application can take from around 5 minutes to 10 minutes
    or more depending on the deploy environment. Have patience!

## Deployment steps

The workflow is [triggered][gh-actions-trigger] with a `push` to the corresponding branch. It also responds to the `workflow_dispatch` event to allow manually triggering via the GitHub Actions UI.

When a deployment workflow runs, the following steps are taken:

### 1. Checkout code

From the tip of the corresponding branch (e.g. `dev`)

### 2. Authenticate to GHCR

Using the `github.actor` and built-in `GITHUB_TOKEN` secret

### 3. Build and push image to GitHub Container Registry (GHCR)

Build the root [`Dockerfile`][dockerfile], tagging with both the branch name (e.g. `dev`) and the SHA from the HEAD commit.

Push this image:tag into [GHCR][ghcr].

### 4. App Service deploy

Each Azure App Service slot is configured to [listen to a webhook from GitHub, then deploy the image][webhook].

[deploy]: https://github.com/cal-itp/benefits/blob/dev/.github/workflows/deploy.yml
[dockerfile]: https://github.com/cal-itp/benefits/blob/dev/Dockerfile
[ghcr]: https://github.com/features/packages
[gh-actions-trigger]: https://docs.github.com/en/actions/reference/events-that-trigger-workflows
[webhook]: https://docs.microsoft.com/en-us/azure/app-service/deploy-ci-cd-custom-container
