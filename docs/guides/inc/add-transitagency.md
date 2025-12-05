1. Cal-ITP creates a new `TransitAgency` in the Admin:
   - <mark>_Typically performed by transit provider's Account Manager_</mark>
   - Once the code changes above are in place <mark>after the `rc` release</mark>, add a new transit agency with the following:
     - Slug: Choose the one added in code
     - Short name, long name, info URL, phone, and supported card schemes: Get from their enrollment form
     - <mark>Eligibility api config:</mark>
     - <mark>Staff group:</mark>
     - <mark>Customer service group:</mark>
     - Logo: Typically found attached to a GitHub issue comment
     - Active: Leave **unchecked** for now
