# Documentation

This website is built using [`mkdocs`](https://www.mkdocs.org/) from the contents of the `dev` (default) branch.

The [`mkdocs.yml`][mkdocs.yml] file in the repository root configures the build process, including the available plugins.

## Editing

All content lives under the [`docs/`][docs] directory in the repository.

To add new sections/articles, create new directories and files under the `docs/` directory, in Markdown format.

The pencil icon is a shortcut to quickly edit the content of the page you are viewing on the website:

![Screenshot showing edit pencil](img/edit-pencil.png)

_Above: Screenshot showing the edit pencil circled in red_

## Features

- [Material for MkDocs: Reference](https://squidfunk.github.io/mkdocs-material/reference/)

  See `mkdocs.yml` for enabled plugins/features

- [Mermaid](https://mermaid-js.github.io/mermaid/)

  Use code fences with `mermaid` type to render Mermaid diagrams within docs. For example, this markdown:

  ````markdown
  ```mermaid
  graph LR
      Start --> Stop
  ```
  ````

  Yields this diagram:

  ```mermaid
  graph LR
      Start --> Stop
  ```

## Running locally

The documentation website can be run locally using Docker Compose:

```bash
# from inside the .devcontainer/ directory
docker compose up docs
```

The site is served from `http://localhost` at a port dynamically assigned by Docker. See
[Docker dynamic ports](./docker-dynamic-ports.md) for more information.

The website is automatically rebuilt as changes are made to `docs/` files.

### In the Devcontainer

When running the [Devcontainer](./development.md#vs-code-with-devcontainers), the docs site is automatically started.

See [Docker dynamic ports](./docker-dynamic-ports.md) for more information on accessing the site on localhost.

## Deploying

A [GitHub Action][mkdocs-action] watches for pushes to `dev`, and uses
[`mhausenblas/mkdocs-deploy-gh-pages`][mkdocs-deploy-gh-pages] to build the `mkdocs` content, force-pushing to the `gh-pages`
branch. At that point, GitHub Pages redeploys the docs site.

[docs]: https://github.com/cal-itp/benefits/tree/dev/docs
[mkdocs.yml]: https://github.com/cal-itp/benefits/blob/dev/mkdocs.yml
[mkdocs-action]: https://github.com/cal-itp/benefits/blob/dev/.github/workflows/mkdocs.yml
[mkdocs-deploy-gh-pages]: https://github.com/mhausenblas/mkdocs-deploy-gh-pages
