# Configuring a new transit agency

Before starting any configuration, the Cal-ITP team and transit agency staff should have a kickoff meeting to confirm that information provided is complete, implementation plan is feasible, and any approvals needed have been obtained.

Then, the following steps are done by the Cal-ITP team to configure a new transit agency in the Benefits application.

Note that a `TransitAgency` model requires:

- a list of supported `EligibilityType`s
- a list of `EligibilityVerifier`s used to verify one of those supported eligibility types
- a `PaymentProcessor` for enrolling the user's contactless card for discounts
- an `info_url` and `phone` for users to contact customer service
- an SVG or PNG file of the transit agency's logo

Also note that these steps assume the transit agency is using Littlepay as their payment processor. Support for integration with [other payment processors](https://www.camobilitymarketplace.org/contracts/) may be added in the future.

## Configuration for development and testing

For development and testing, only a Littlepay customer group is needed since there is no need to interact with any discount product. (We don't have a way to tap a card against the QA system to trigger a discount and therefore have no reason to associate the group with any product.)

### Steps

1. Cal-ITP uses the transit agency's Littlepay merchant ID to create a customer group in the Littlepay QA environment for each type of eligibility (e.g. senior).
1. For each group that's created, a group ID will be returned and should be set as the `group_id` on a new `EligibilityType` in the Benefits database. (See [Configuration data](../data/) for more on loading the database.)
1. Cal-ITP creates a new `EligibilityVerifier` in the database for each supported eligibility type. This will require configuration for either [API](https://docs.calitp.org/eligibility-api/specification/)-based verification or verification through an [OAuth Open ID Connect provider](../oauth/) (e.g. sandbox Login.gov) -- either way, this resource should be meant for testing.
1. Cal-ITP creates a new `TransitAgency` in the database and associates it with the new `EligibilityType`s and `EligibilityVerifier`s as well as the existing Littlepay `PaymentProcessor`.

## Configuration for production validation

For production validation, both a customer group and discount product are needed. The customer group used here is a temporary one for testing only. Production validation is done against the Benefits test environment to avoid disruption of the production environment.

### Steps

1. Transit agency staff creates the discount product in production Littlepay (if it does not already exist).
1. Cal-ITP creates a customer group **for testing purposes** in production Littlepay.
1. Cal-ITP associates the group with the product.
1. Cal-ITP sets that group's ID as the `group_id` for a new `EligibilityType` in the Benefits database.
1. Cal-ITP creates a new `EligibilityVerifier` with configuration **for a testing environment** to ensure successful eligibility verification. (For example, use sandbox Login.gov instead of production Login.gov.)
1. Cal-ITP creates a new `TransitAgency` in the database with the proper associations to eligibility types, verifiers, and payment processor.

At this point, Cal-ITP and transit agency staff can coordinate to do on-the-ground testing where a live card is tapped on a live payment validator.

### Production validation testing

1. Transit agency staff (or Cal-IT staff) does live test in the field.
1. Transit agency staff uses the Merchant Portal to verify the taps and discounts were successful.
1. Cal-ITP uses logs from Azure to verify the user was associated to the customer group.
1. Cal-ITP verifies that Amplitude analytic events are being sent.

## Configuration for production

Once production validation is done, the transit agency can be added to the production Benefits database.

### Steps

1. Cal-ITP creates a customer group **for production use** in production Littlepay.
1. Cal-ITP associates the group with the discount product created [previously during production validation](#configuration-for-production-validation).
1. Cal-ITP sets that group's ID as the `group_id` for a new `EligibilityType` in the Benefits database.
1. Cal-ITP creates a new `EligibilityVerifier` with configuration for the **production** eligibility verification system.
1. Cal-ITP creates a new `TransitAgency` in the database with proper associations to eligibility types, verifiers, and payment processor.

### Cleanup

At this point, the customer group that was created in production Littlepay for testing purposes can be deleted.

1. Remove the association between the test customer group and discount product.
1. Delete the test customer group.
