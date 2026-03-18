# Testing Self-Service enrollment

Testing the Self-Service Enrollment featureset refers to using the Benefits app as a _member of the public_, and
stepping through the process of Self-Service Enrollment for one or more enrollment flows.

## When to test

- When refactoring/functional changes are introduced to the Self-Service Enrollment featureset.
- When new copy or UI elements are introduced for the Self-Service Enrollment featureset.
- When onboarding a new agency.

## Scenarios

The following scenarios should be reviewed at a minimum. Look out for issues with the user session and interaction with
eligibility verification systems (Eligibility Servers and Identity Gateway) and transit processor systems. Ensure enrollment
events are being accurately captured in the Benefits Administrator.

- Following a **Login.gov** enrollment pathway to completion.
  - Also review when a user _is not eligible_.
- Following a **Medicare.gov** enrollment pathway to completion.
  - Also review when a user _is not eligible_.
- Following an **Agency Card** pathway to completion.
  - Also review when a user _is not eligible_.
- Following a grouped agency enrollment to completion
- Following a Littlepay enrollment to completion
- Following a Switchio enrollment to completion
