# Linting and pre-commit

## Formatting

[`black`][black] provides Python code formatting via the [`ms-python.python`][python] VS Code extension.

[`prettier`][prettier] provides code formatting for front-end (CSS/JavaScript) via the [`esbenp.prettier-vscode`][esbenp.prettier-vscode] VS Code extension.

See the `.vscode/settings.json` file for more information on how this is configured in [the devcontainer][devcontainer].

## Linting

[`flake8`][flake8] provides Python code linting via the [`ms-python.python`][python] VS Code extension.

See the `.vscode/settings.json` file for more information on how this is configured in [the devcontainer][devcontainer].

## pre-commit

This repository uses [`pre-commit`][pre-commit] hooks to check and format code. The `.pre-commit-config.yaml` file defines a
number of `pre-commit` hooks, including `black`, `flake8`, line ending and whitespace checkers, and more.

`pre-commit` is installed and activated within [the devcontainer][devcontainer] and runs automatically with each commit.

Branch protection rules on the environment branches in GitHub ensure that `pre-commit` checks have passed before a merge is
allowed. See the workflow file at `.github/workflows/pre-commit.yml`.

[black]: https://github.com/psf/black
[devcontainer]: ./README.md
[esbenp.prettier-vscode]: https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode
[flake8]: https://flake8.pycqa.org/en/latest/
[ms-python.python]: https://marketplace.visualstudio.com/items?itemName=ms-python.python
[prettier]: https://prettier.io/
[pre-commit]: https://pre-commit.com/
