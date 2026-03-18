# Testing in-person enrollment

Testing the In-Person Enrollment featureset refers to logging in to the Benefits Administrator as a _Transit Agency user_, and
stepping through the process of In-Person Enrollment for one or more enrollment flows.

## When to test

- When refactoring/functional changes are introduced to the In-Person Enrollment featureset.
- When new copy or UI elements are introduced for the In-Person Enrollment featureset.
- When significant refactoring/functional changes are introduced to the Self-Service Enrollment featureset.

## Scenarios

The following scenarios should be reviewed at a minimum. Look out for issues with the user session and interaction with transit
processor systems. Ensure enrollment events are being accurately captured in the Benefits Administrator.

- Following a Littlepay enrollment to completion
- Following a Switchio enrollment to completion
- Back-to-back enrollments for either Littlepay or Switchio (e.g. starting a new enrollment immediately after finishing one)
