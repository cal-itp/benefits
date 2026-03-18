# Smoke testing

[Smoke testing](<https://en.wikipedia.org/wiki/Smoke_testing_(software)>) is a form of quality assurance testing meant to

> ...reveal simple failures severe enough to, for example, reject a prospective software release.

Smoke testing always occurs in the `production` Benefits application immediately following a new release. Because of this, we
cannot necessarily complete an entire enrollment flow and exercise all parts of the application.

## When to test

Whenever a new feature or major refactor is introduced for the Benefits or Eligibility Server applications, the Smoke Testing
procedures should be followed.

Some examples of new features or major refactors that would trigger a need for Smoke Testing include but are not necessarily limited to:

- A new enrollment pathway is launched
- A new transit agency is launched
- A new payment processor integration is launched
- A refactor of an integration with an external service (i.e. Eligibility Server, Identity Gateway, payment processor)
- A refactor of the underlying data model
- A significant refactor or redesign of the User Interface and/or User Experience (i.e. the steps a user takes through an enrollment pathway)

## Follow-up

### If Smoke Testing reveals no critical flaws?

Upon successful completion of the Smoke Test (i.e. no critical flaws are discovered), the tester should leave a comment
indicating such on the corresponding Release issue in GitHub.

Upon receiving this comment, the Release Manager for this release may close the Release issue and mark the release as complete.

### If Smoke Testing reveals critical flaws?

A critical flaw would include instances where the Benefits app is unable to communicate with an external service due to
programming or configuration errors. If critical flaws are found that would require code changes to fix, the release should be
rolled back while the errors are investigated and ultimately patched in the `test` and/or `dev` environments, before another
release and round of Smoke Testing into `production`.

If the `production` environment can be restored to expected functionality by changing configuration, then a code rollback may
not be necessary. Make the configuration change ASAP to prevent exposing the issue to users while it’s investigated and
corrected in lower environments.

## Setup for Smoke Testing

In order to minimize the impact of Smoke Testing on the Benefits analytics and metrics calculations, testers must first
**modify their browser’s User Agent String**, which will allow for easy filtering of events corresponding to these tests.

The following article outlines the procedure for all major desktop browsers (Chrome, Edge, Firefox, Safari), and this can be
done without any browser extensions or plugins:

<https://geekflare.com/change-user-agent-in-browser/>

There are also a number of extensions that support easier switching of User Agent Strings for certain browsers:

- [Firefox](https://addons.mozilla.org/en-US/firefox/addon/modify-header-value/)
- [Chrome](https://chrome.google.com/webstore/detail/user-agent-switcher-for-c/djflhoibgkdhkhhcedjiklpkjnoahfmg)
- [Chrome](https://chromewebstore.google.com/detail/user-agent-switcher-and-m/bhchdcejhohfmigjafbampogmaanbfkg) (another one that can be configured per-domain)

Testers should modify their browser’s User Agent String to the following value before proceeding:

```console
cal-itp/benefits-smoke-test
```

## Scenarios

### Self-Service

- **Login.gov** enrollment flow using a _real personal Login.gov account_
  - Expect to be redirected to the "not eligible" page
- **Medicare.gov** enrollment flow
  - Expect to be redirected to Medicare.gov homepage
- **MST Courtesy Cards** enrollment flow using sample data
  - Expect to be redirected to the "not eligible" page
- **MST Courtesy Cards** enrollment flow using `MST Courtesy Card (for testing)` in LastPass
  - Expect to be verified as eligible
  - Enroll business credit card with Littlepay
  - See success screen
- **SBMTD Reduced Fare Mobility ID** enrollment flow using sample data
  - Expect to be redirected to the "not eligible" page
- **SBMTD Reduced Fare Mobility ID** enrollment flow using `SBMTD Reduced Fare Mobility ID (for testing)` in LastPass
  - Expect to be verified as eligible
  - Enroll business credit card with Littlepay
  - See success screen
- Select a **grouped agency**
  - Expect to see the group overview page before continuing to eligibility

### In-Person

- Sign in to the Benefits Administrator as the **`mst-user`** (in LastPass) and complete any enrollment flow
  - Enroll business credit card with Littlepay
  - Expect to see the success screen
