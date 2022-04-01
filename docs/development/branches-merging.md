# Branches and merging

The default GitHub branch is `dev`. All new feature work should be in the form of Pull Requests (PR) that target `dev` as their
base.

In addition to `dev`, the repository has three other long-lived branches:

* `test` and `prod` correspond to the Test and Production [deploy environments](../deployment/README.md), respectively.
* `gh-pages` hosts the compiled documentation, and is always forced-pushed by the
[docs build process](../getting-started/documentation.md#deploying).

[Branch protection rules][gh-branch-protection] are in place on three environment branches (`dev`, `test`, `prod`) to:

* Prevent branch deletion
* Restrict force-pushing, where appropriate
* Require passing status checks before merging into the target branch is allowed

Merging of PRs should be done using the *merge commit* strategy. The *squash* strategy is also enabled for particularly wild or
messy PRs, but this should only be used as a last resort when it is not possible or too difficult to rebase the PR branch onto
the target branch before merging.

When merging a PR into `dev`, it is customary to format the merge commit message like:

```console
Title of PR (#number)
```

instead of the default:

```console
Merge pull request #number from source-repo/source-branch
```

Application deployments occur automatically when a PR is merged to the target environment branch. A successful deploy to
`dev` is required before a deploy to `test` is allowed; a successful deploy to `test` is required before a deploy to `prod` is
allowed.

See [Deployment](../deployment/README.md) for more information.

[gh-branch-protection]: https://docs.github.com/en/github/administering-a-repository/defining-the-mergeability-of-pull-requests/about-protected-branches
