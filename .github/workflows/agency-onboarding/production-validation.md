## Acceptance criteria

_The following configuration always happens in the Benefits `test` environment._

- [ ] Create `TransitAgency` instance
- [ ] Create `{{TRANSIT_PROCESSOR}}Config` instance
  - [ ] Mark the environment as `production`
  - [ ] (Littlepay only) use API credentials for the agency's Littlepay `production` instance
  - [ ] (Switchio only) use API credentials for the agency's Switchio `acceptance` instance
- [ ] Create `EnrollmentFlow` instance(s)
- [ ] Create `{{TRANSIT_PROCESSOR}}Group` instance(s) using group ID(s) from the agency's {{TRANSIT_PROCESSOR}} `production` instance
  - (Switchio only) the group IDs are shared among all agencies (e.g. `MEDICARE`)
- [ ] Return to `TransitAgency` instance and check the **Active** box
