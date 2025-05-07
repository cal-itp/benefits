1. Cal-ITP creates new `EnrollmentFlow`s in the Admin:
   - For each type of discount the new transit provider will be using, add an enrollment flow with the following:
     - System name
     - Label (retype the system name)
     - Choose the `TransitAgency` that was just created
     - Modify supported enrollment methods, if necessary
     - Choose the appropriate OAuth config (e.g., benefits-logingov for an Older Adults flow)
     - Choose the appropriate claims request
   - All other fields can likely be skipped or left at their default value.
