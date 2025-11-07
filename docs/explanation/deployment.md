# Deployment

The Benefits app is currently deployed into a Microsoft Azure account provided by [California Department of Technology (CDT)'s Office of Enterprise Technology (OET)][oet], a.k.a. the "DevSecOps" team. More specifically, it uses [custom containers][app-service-containers] on [Azure App Service][app-service]. [More about the infrastructure.](infrastructure.md)

## Deployment process

The Django application gets built into a [Docker image][dockerfile] with [NGINX](https://www.nginx.com/) and
[Gunicorn](https://gunicorn.org/). SQLite is used within that same container to store configuration data; there is no external database.

The application is deployed to an [Azure Web App Container][az-webapp] using three separate environments for `dev`, `test`,
and `prod`.

The [Deploy][deploy-workflow] workflow is responsible for building that branch's image and pushing to [GitHub Container
Registry (GHCR)][ghcr]. It also deploys to the Azure Web App, telling Azure to restart the app and pull the latest image.

You can view what Git commit is deployed for a given environment by visiting the URL path `/static/sha.txt`.

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

## Configuration

Sensitive [configuration settings](configuration.md) are maintained as Application Configuration variables in Azure,
referencing [Azure Key Vault secrets](https://azure.microsoft.com/en-us/products/key-vault/). Other non-sensitive configuration is maintained directly in the configuration database via the [Django Admin](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/).

## Docker images

Docker images for each of the deploy branches are available from GitHub Container Registry (GHCR):

- [Repository Package page](https://github.com/cal-itp/benefits/pkgs/container/benefits)
- Image path: `ghcr.io/cal-itp/benefits`

[oet]: https://techblog.cdt.ca.gov/2020/06/cdt-taking-the-lead-in-digital-transformation/
[app-service-containers]: https://docs.microsoft.com/en-us/azure/app-service/configure-custom-container
[app-service]: https://docs.microsoft.com/en-us/azure/app-service/overview
[deploy-workflow]: https://github.com/cal-itp/benefits/blob/main/.github/workflows/deploy.yml
[az-webapp]: https://azure.microsoft.com/en-us/services/app-service/containers/
[ghcr]: https://github.com/features/packages
[deploy]: https://github.com/cal-itp/benefits/blob/main/.github/workflows/deploy.yml
[dockerfile]: https://github.com/cal-itp/benefits/blob/main/appcontainer/Dockerfile
[gh-actions-trigger]: https://docs.github.com/en/actions/reference/events-that-trigger-workflows
