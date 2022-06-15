# Commits, branches, and merging

## Commits

This project enforces the [Conventional Commits][conventional-commits] style for commit message formatting:

```
<type>[(optional-scope)]: <description>

[optional body]
```

Where `<type>` indicates the nature of the commit, one of a list of possible values:

* `build` - related to the build or compile process
* `chore` - administrative tasks, cleanups, dev environment
* `ci` - related to automated builds/tests etc.
* `docs` - updates to the documentation
* `feat` - new code, features, or interfaces
* `fix` - bug fixes
* `perf` - performance improvements
* `refactor` - non-breaking logic refactors
* `revert` - undo a prior change
* `style` - code style and formatting
* `test` - having to do with testing of any kind

E.g.

```bash
git commit -m "feat(eligibility/urls): add path for start"
```

## Branches

The default GitHub branch is `dev`. All new feature work should be in the form of Pull Requests (PR) that target `dev` as their
base.

In addition to `dev`, the repository has three other long-lived branches:

* `test` and `prod` correspond to the Test and Production [deploy environments](../deployment/README.md), respectively.
* `gh-pages` hosts the compiled documentation, and is always forced-pushed by the
[docs build process](../getting-started/documentation.md#deploying).

### Protection rules

[Branch protection rules][gh-branch-protection] are in place on three environment branches (`dev`, `test`, `prod`) to:

* Prevent branch deletion
* Restrict force-pushing, where appropriate
* Require passing status checks before merging into the target branch is allowed

### PR branches

PR branches are typically named with a [conventional type][conventional-commits] prefix, a slash `/`, and then descriptor in `lower-dashed-case`:

```bash
<type>/<lower-dashed-descriptor>
```

E.g.

```bash
git checkout -b feat/verifier-radio-buttons
```

and

```bash
git checkout -b refactor/verifier-model
```

PR branches are deleted once their PR is merged.

## Merging

Merging of PRs should be done using the *merge commit* strategy. The PR author should utilize `git rebase -i` to ensure
their PR commit history is clean, logical, and free of typos.

When merging a PR into `dev`, it is customary to format the merge commit message like:

```console
Title of PR (#number)
```

instead of the default:

```console
Merge pull request #number from source-repo/source-branch
```

[conventional-commits]: https://www.conventionalcommits.org/en/v1.0.0/
[gh-branch-protection]: https://docs.github.com/en/github/administering-a-repository/defining-the-mergeability-of-pull-requests/about-protected-branches
