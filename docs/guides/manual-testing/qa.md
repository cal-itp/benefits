# QA testing

Quality Assurance (QA) testing is meant to verify common and edge-case user flows through the software to validate assumptions
about its basic level of functionality.

It is important that QA testing include evaluation of both the self-service and in-person enrollment featuresets. As they share
much underlying code, it can be easy to overlook knock-on effects when e.g. working on self-service that could impact in-person.

Testing the Self-Service Enrollment featureset refers to using the Benefits app as a _member of the public_, and stepping
through the process of Self-Service Enrollment for one or more enrollment flows.

Testing the In-Person Enrollment featureset refers to logging in to the Benefits Administrator as a _Transit Agency user_, and
stepping through the process of In-Person Enrollment for one or more enrollment flows.

## When to test

- When refactoring/functional changes are introduced to the Self-Service Enrollment featureset.
- When new copy or UI elements are introduced for the Self-Service Enrollment featureset.
- When refactoring/functional changes are introduced to the In-Person Enrollment featureset.
- When new copy or UI elements are introduced for the In-Person Enrollment featureset.
- When onboarding a new agency.

## Scenarios

Look out for issues with the user session and interaction with eligibility verification systems (Eligibility Servers and Identity Gateway) and transit processor systems. Ensure enrollment events are being accurately captured in the Benefits Administrator.

The following Markdown snippet lists the scenarios for QA testing.

Use this snippet to draft a comment for QA testing in the Release issue.

```markdown
## QA testing in `test`

- [ ] Self-service Login.gov enrollment flow
  - [ ] Not eligible
  - [ ] Eligible, enrolled
- [ ] Self-service Medicare.gov enrollment flow
  - [ ] Not eligible
  - [ ] Eligible, enrolled
- [ ] Self-service MST Courtesy Cards
  - [ ] Not eligible
  - [ ] Eligible, enrolled
- [ ] Self-service SBMTD Reduced Fare Mobility ID
  - [ ] Not eligible
  - [ ] Eligible, enrolled
- [ ] Self-service expiring discount
  - [ ] Not eligible
  - [ ] Eligible, enrolled
  - [ ] Eligible, already enrolled, before re-enrollment window
- [ ] Self-service select a grouped agency
- [ ] In-person select a grouped agency
- [ ] In-person enrollment with Littlepay
- [ ] In-person enrollment with Switchio
- [ ] Back-to-back In-person enrollments
```
