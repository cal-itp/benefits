# Making a rollback release

This list outlines the manual steps needed to make a rollback of the
`benefits` app.

If a change is deployed to the app that makes it fail to start, making a rollback
will deploy the app to a known working state again.

[Start a new Release on Github](https://github.com/cal-itp/benefits/issues/new?labels=release&template=release.yml&title=Make+a+Release){ .md-button }

## 0. Create a release tag on the commit associated with the last known good release tag

```bash
git tag -a YYYY.0M.R <commit-hash>
```

Replace `YYYY.0M.R` with the rollback version and `<commit-hash>` with the hash of the commit associated with the last known good release tag. Git will open your default text editor and prompt you for the tag annotation. For the tag annotation,
use the version of the release tag for the rollback and close the text editor.

## 1. Push the tag to GitHub to kick off the rollback

```bash
git push origin YYYY.0M.R
```

## 2. [Generate release notes](https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes)

Edit release notes with additional context, images, animations, etc. as-needed and link to the Release process issue.
