# Making a hotfix release

This list outlines the manual steps needed to make a hotfix release of the
`benefits` app.

If `main` contains in-progress work that is not yet ready for a release but a simple code fix
is needed in production, a separate process to test the changes before deploying to production must be undertaken.
This is called a hotfix release. Typically, a hotfix release involves a simple code change that can be quickly implemented, in contrast to a [rollback release](./rollback.md), which generally requires more complex code changes which take more time to implement.

[Start a new Release on Github](https://github.com/cal-itp/benefits/issues/new?labels=release&template=release.yml&title=Make+a+Release){ .md-button }

## 0. Create a temporary hotfix branch from the latest release tag

```bash
git checkout -b <hotfix-branch> <release-tag>
```

Replace `<hotfix-branch>` with the hotfix branch name and `<release-tag>` with the latest release tag.

## 1. Fix whatever issue is wrong using the hotfix branch

Commit the code changes that fix the issue that prompted the hotfix.

## 2. Tag the HEAD of the hotfix branch with a release tag

```bash
git tag -a YYYY.0M.R
```

Git will open your default text editor and prompt you for the tag annotation. For the tag annotation,
use the release tag version and close the text editor.

## 3. Push the tag to GitHub to kick off the hotfix

```bash
git push origin YYYY.0M.R
```

## 4. [Generate release notes](https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes)

Edit release notes with additional context, images, animations, etc. as-needed and link to the Release process issue.

## 5. Merge into `main` for the next release

Create a PR to merge the changes from the hotfix branch into `main` for the next release.
