## Acceptance criteria

_The following configuration always happens in the Benefits `production` environment._

- [ ] Create `TransitAgency` instance
- [ ] Create `{{TRANSIT_PROCESSOR}}Config` instance
  - [ ] Mark the environment as `production`
  - [ ] Use API credentials for the agency's {{TRANSIT_PROCESSOR}} `production` instance
- [ ] Create `EnrollmentFlow` instance(s)
- [ ] Create `{{TRANSIT_PROCESSOR}}Group` instance(s) using group ID(s) from the agency's {{TRANSIT_PROCESSOR}} `production` instance
  - (Switchio only) the group IDs are shared among all agencies (e.g. `MEDICARE`)
- [ ] Return to `TransitAgency` instance and check the **Active** box
