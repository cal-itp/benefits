# Configuring a new transit agency

Before starting any configuration, the Cal-ITP team and transit agency staff should have a kickoff meeting to confirm that information provided is complete, implementation plan is feasible, and any approvals needed have been obtained.

Then, the following steps are done by the Cal-ITP team to configure a new transit agency in the Benefits application.

Note that a `TransitAgency` model requires:

- a list of supported `EligibilityType`s
- a list of `EligibilityVerifier`s used to verify one of those supported eligibility types
- a `PaymentProcessor` for enrolling the user's contactless card for discounts

Also note that these steps assume the transit agency is using Littlepay as their payment processor. Support for integration with other payment processors may be added in the future.

## Configuration for development and testing

For development and testing, only a Littlepay customer group is needed since there is no need to interact with any discount product. (We don't have a way to tap a card against the QA system to trigger a discount and therefore have no reason to associate the group with any product.)

### Steps

1. Cal-ITP uses the transit agency's Littlepay merchant ID to create a customer group in the Littlepay QA environment for each type of eligibility (e.g. senior).
1. For each group that's created, a group ID will be returned and should be set as the `group_id` on a new `EligibilityType` in the Benefits database. (See [Configuration data](../data/) for more on loading the database.)
1. Cal-ITP creates a new `EligibilityVerifier` in the database for each supported eligibility type. This will require configuration for either [API](https://docs.calitp.org/eligibility-api/specification/)-based verification or verification through an [OAuth Open ID Connect provider](../oauth/) (e.g. Login.gov).
1. Cal-ITP creates a new `TransitAgency` in the database and associates it with the new `EligibilityType`s and `EligibilityVerifier`s as well as the existing Littlepay `PaymentProcessor`.
