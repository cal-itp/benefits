# Home

This website provides technical documentation for [`benefits`](https://github.com/cal-itp/benefits)
from the [California Integrated Travel Project (Cal-ITP)](https://www.calitp.org).

Documentation for the `main` branch is available online at: <https://docs.calitp.org/benefits>.

## Editing documentation

Docs content all lives under `docs/`, with some top-level configuration for how the website is built under `mkdocs.yml`.
To add new sections/articles, simply create new directories/files under `docs/` in Markdown format.

## Documentation features

- [Material for MkDocs: Reference](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)

    See `mkdocs.yml` for enabled plugins/features

- [Mermaid](https://mermaid-js.github.io/mermaid/)

    Use code fences with `mermaid` type to render Mermaid diagrams within docs. For example, this markdown:

    ~~~markdown
    ```mermaid
    graph LR
        Start --> Stop
    ```
    ~~~

    Yields this diagram:

    ~~~mermaid
    graph LR
        Start --> Stop
    ~~~
