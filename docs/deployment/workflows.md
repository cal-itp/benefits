# Workflows

There are three different GitHub Actions deployment workflows, one for each environment:

* [`.github/workflows/deploy-dev.yml`][deploy-dev]
* [`.github/workflows/deploy-test.yml`][deploy-test]
* [`.github/workflows/deploy-prod.yml`][deploy-prod]

!!! info

    The entire process from GitHub commit to full redeploy of the application can take from around 5 minutes to 10 minutes
    or more depending on the deploy environment. Have patience!

## Deployment steps

Each of the three workflows are [triggered][gh-actions-trigger] with a `push` to the corresponding branch. Each workflow also
responds to the `workflow_dispatch` event to allow manually triggering via the GitHub Actions UI.

When a deployment workflow runs, the following steps are taken:

### 1. Checkout code

From the tip of the corresponding branch (e.g. `dev`)

### 2. Authenticate to GHCR

Using the `github.actor` and built-in `GITHUB_TOKEN` secret

### 3. Build and push image to GHCR

Build the root [`Dockerfile`][Dockerfile], tagging with both the branch name (e.g. `dev`) and the SHA from the HEAD commit.

Push this image:tag into [GHCR][ghcr].

[deploy-dev]: https://github.com/cal-itp/benefits/blob/dev/.github/workflows/deploy-dev.yml
[deploy-test]: https://github.com/cal-itp/benefits/blob/dev/.github/workflows/deploy-test.yml
[deploy-prod]: https://github.com/cal-itp/benefits/blob/dev/.github/workflows/deploy-prod.yml
[dockerfile]: https://github.com/cal-itp/benefits/blob/dev/Dockerfile
[ghcr]: https://github.com/features/packages
[gh-actions-trigger]: https://docs.github.com/en/actions/reference/events-that-trigger-workflows
