# Overview

The Benefits app is currently deployed into a Microsoft Azure account provided by [California Department of Technology (CDT)'s Office of Enterprise Technology (OET)][oet], a.k.a. the "DevSecOps" team. More specifically, it uses [custom containers][app-service-containers] on [Azure App Service][app-service]. [More about the infrastructure.](infrastructure.md)

## Deployment process

The Django application gets built into a [Docker image][dockerfile] with [NGINX](https://www.nginx.com/) and
[Gunicorn](https://gunicorn.org/). SQLite is used within that same container to store configuration data; there is no external database.

The application is deployed to an [Azure Web App Container][az-webapp] using three separate environments for `dev`, `test`,
and `prod`.

The [Deploy](deploy-workflow) workflow is responsible for building that branch's image and pushing to [GitHub Container
Registry (GHCR)][ghcr]. It also deploys to the Azure Web App, telling Azure to restart the app and pull the latest image.

You can view what Git commit is deployed for a given environment by visiting the URL path `/static/sha.txt`.

## Configuration

Sensitive [configuration settings](../configuration/README.md) are maintained as Application Configuration variables in Azure,
referencing [Azure Key Vault secrets](https://azure.microsoft.com/en-us/products/key-vault/). Other non-sensitive configuration
is maintained directly in the configuration database via the [Django Admin](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/).

## Docker images

Docker images for each of the deploy branches are available from GitHub Container Registry (GHCR):

- [Repository Package page](https://github.com/cal-itp/benefits/pkgs/container/benefits)
- Image path: `ghcr.io/cal-itp/benefits`

[oet]: https://techblog.cdt.ca.gov/2020/06/cdt-taking-the-lead-in-digital-transformation/
[app-service-containers]: https://docs.microsoft.com/en-us/azure/app-service/configure-custom-container
[app-service]: https://docs.microsoft.com/en-us/azure/app-service/overview
[deploy-workflow]: https://github.com/cal-itp/benefits/blob/main/.github/workflows/deploy.yml
[dockerfile]: https://github.com/cal-itp/benefits/blob/main/Dockerfile
[az-webapp]: https://azure.microsoft.com/en-us/services/app-service/containers/
[ghcr]: https://github.com/features/packages
