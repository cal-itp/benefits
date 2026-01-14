# Admin interface

## Adding a new user

- Add the user's email to either `GOOGLE_SSO_STAFF_LIST` or `GOOGLE_SSO_SUPERUSER_LIST` depending on what permissions they should have.
  - The email must be from a domain that is in the `GOOGLE_SSO_ALLOWABLE_DOMAINS` list.
- Restart the Benefits application so that Django settings are re-loaded.
- Have the user log in to the admin interface with their Google account.
