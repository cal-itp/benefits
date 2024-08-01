# Making a regular release

This list outlines the manual steps needed to make a new release of the
`benefits` app.

A release is made by pushing an annotated tag. The name of the tag must use
the version number format mentioned below. This kicks off a deployment to the
production environment and creates a GitHub release. The version number for the
app and the release will be the tag’s name. More details on the deployment steps
can be found under [Workflows](./workflows.md).

The list of releases can be found on the [repository Releases page](https://github.com/cal-itp/benefits/tags)
on GitHub.

[Start a new Release on Github](https://github.com/cal-itp/benefits/issues/new?labels=release&template=release.yml&title=Make+a+Release){ .md-button }

## 0. Decide on the new version number

A new release implies a new version.

`benefits` uses the [CalVer](https://calver.org/) versioning scheme, where
version numbers look like: `YYYY.0M.R`

- `YYYY` is the 4-digit year of the release; e.g. `2021`, `2022`
- `0M` is the 2-digit, 0-padded month of the release; e.g. `02` is February, `12`
  is December.
- `R` is the 1-based release counter for the given year and month;
  e.g. `1` for the first release of the month, `2` for the second, and so on.

Version numbers for release candidates append `-rcR`, where `R` is the 1-based release counter for the anticipated release. For example, the first release candidate for the `2024.01.1` release would be `2024.01.1-rc1`.

## 1. Create a release candidate tag on `main` and push it

```bash
git fetch
git checkout main
git reset --hard origin/main
git tag -a YYYY.0M.R-rcR
```

Git will open your default text editor and prompt you for the tag annotation. For the tag annotation, use the release candidate version. Finally, after closing the text editor:

```bash
git push origin YYYY.0M.R-rcR
```

This builds a new package and deploys to the Azure test environments. No GitHub release is created for release candidates.

## 2. Create a release tag on `main` and push it

```bash
git fetch
git checkout main
git reset --hard origin/main
git tag -a YYYY.0M.R
```

Git will open your default text editor and prompt you for the tag annotation. For the tag annotation, use the title of the Release process issue that kicked off the release. Finally, after closing the text editor:

```bash
git push origin YYYY.0M.R
```

This builds the package and deploys to the Azure production environments. A GitHub release is created.

## 3. [Generate release notes](https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes)

Edit release notes with additional context, images, animations, etc. as-needed and link to the Release process issue.
