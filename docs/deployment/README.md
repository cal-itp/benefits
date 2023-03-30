# Overview

[dev-benefits.calitp.org][dev-benefits] is currently deployed into a Microsoft Azure account provided by [California Department of Technology (CDT)'s Office of Enterprise Technology (OET)][oet], a.k.a. the "DevSecOps" team. More specifically, it uses [custom containers][app-service-containers] on [Azure App Service][app-service]. [More about the infrastructure.](infrastructure.md)

## Deployment process

The Django application gets built into a [Docker image][dockerfile] with [NGINX](https://www.nginx.com/) and
[Gunicorn](https://gunicorn.org/). SQLite is used within that same container to store configuration data; there is no external database.

The application is deployed to an [Azure Web App Container][az-webapp] using three separate environments for `dev`, `test`,
and `prod`.

A [GitHub Action][gh-actions] per environment is responsible for building that branch's image and pushing to [GitHub Container
Registry (GHCR)][ghcr].

GitHub POSTs a [webhook][gh-webhooks] to the Azure Web App when an [image is published to GHCR][gh-webhook-event], telling
Azure to restart the app and pull the latest image.

You can view what Git commit is deployed for a given environment by visitng the URL path `/static/sha.txt`.

## Configuration

[Configuration settings](../configuration/README.md) are stored as Application Configuration variables in Azure.
[Data](../configuration/data.md) is loaded via Django data migrations.

## Docker images

Docker images for each of the deploy branches are available from GitHub Container Registry (GHCR):

* [Repository Package page](https://github.com/cal-itp/benefits/pkgs/container/benefits)
* Image path: `ghcr.io/cal-itp/benefits`
* Image tags: `dev`, `test`, `prod`

[dev-benefits]: https://dev-benefits.calitp.org
[oet]: https://techblog.cdt.ca.gov/2020/06/cdt-taking-the-lead-in-digital-transformation/
[app-service-containers]: https://docs.microsoft.com/en-us/azure/app-service/configure-custom-container
[app-service]: https://docs.microsoft.com/en-us/azure/app-service/overview
[dockerfile]: https://github.com/cal-itp/benefits/blob/dev/Dockerfile
[az-webapp]: https://azure.microsoft.com/en-us/services/app-service/containers/
[gh-actions]: https://docs.github.com/en/actions
[gh-webhook-event]: https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#package
[gh-webhooks]: https://docs.github.com/en/github-ae@latest/developers/webhooks-and-events/webhooks
[ghcr]: https://github.com/features/packages
