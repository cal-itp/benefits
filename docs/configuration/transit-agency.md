# Configuring a new transit agency

Before starting any configuration, the Cal-ITP team and transit agency staff should have a kickoff meeting to confirm that information provided is complete, implementation plan is feasible, and any approvals needed have been obtained.

Then, the following steps are done by the Cal-ITP team to configure a new transit agency in the Benefits application.

Note that a `TransitAgency` model requires:

- a list of `EnrollmentFlows`s available to the agency's users
- a `TransitProcessor` for enrolling the user's contactless card for discounts
- an `info_url` and `phone` for users to contact customer service
- an SVG or PNG file of the transit agency's logo
- HTML templates for various buttons, text and other user interface elements of the flow, including:
  - `index_template`: _Required for agencies_ - Text for agency direct entry page
  - `eligibility_index_template`: _Required for agencies_ - Text for Eligibility Index page
  - `selection_label_template`: _Required for enrollment flows_ - Text and optional modals for the radio button form on the Eligibility Index page
  - `eligibility_start_template`: _Required for enrollment flows_ - Text and optional custom styles for call to action button on the Eligibility Start page
  - `enrollment_success_template`: _Required for agencies_ - Text for Enrollment Success page
  - `help_template`: _Required for agencies_ - Agency-specific help questions and answers
  - `sign_out_button_template`: _Required for claims providers_ - Sign out link button, used on any page after sign in
  - `sign_out_link_template`: _Required for claims providers_ - Sign out link text, used on any page after sign in

Also note that these steps assume the transit agency is using Littlepay as their transit processor. Support for integration with [other transit processors](https://www.camobilitymarketplace.org/contracts/) may be added in the future.

## Configuration for development and testing

For development and testing, only a Littlepay customer group is needed since there is no need to interact with any discount product. (We don't have a way to tap a card against the QA system to trigger a discount and therefore have no reason to associate the group with any product.)

### Steps

1. Cal-ITP uses the transit agency's Littlepay merchant ID to create a customer group in the Littlepay QA environment for each type of eligibility (e.g. senior).
1. For each group that's created, a group ID will be returned and should be set as the `group_id` on a new `EnrollmentFlow` in the Benefits database. (See [Configuration data](../data/) for more on loading the database.)
1. Cal-ITP creates a new `EnrollmentFlow` in the database for each supported eligibility type. This will require configuration for either [API](https://docs.calitp.org/eligibility-api/specification/)-based verification or verification through an [OAuth Open ID Connect claims provider](../oauth/) (e.g. sandbox Login.gov) -- either way, this resource should be meant for testing.
1. Cal-ITP creates a new `TransitAgency` in the database and associates it with the new `EnrollmentFlow`s as well as the existing Littlepay `TransitProcessor`.

## Configuration for production validation

For production validation, both a customer group and discount product are needed. The customer group used here is a temporary one for testing only. Production validation is done against the Benefits **test environment** to avoid disruption of the production environment.

### Steps

1. Transit agency staff creates the discount product in production Littlepay (if it does not already exist).
1. Transit agency staff takes a screenshot of the discount product in the Merchant Portal, making sure the browser URL is visible, and sends that to Cal-ITP.
1. Cal-ITP creates a customer group **for testing purposes** in production Littlepay.
1. Cal-ITP associates the group with the product.
1. Cal-ITP creates a new `EnrollmentFlow` **for testing purposes** in the Benefits database and sets the `group_id` to the ID of the newly-created group.
1. Cal-ITP configures the newly created `EnrollmentFlow` **for a testing environment** to ensure successful eligibility verification. (For example, use sandbox Login.gov instead of production Login.gov.)
1. Cal-ITP creates a new `TransitProcessor` **for testing purposes** with configuration for production Littlepay.
1. Cal-ITP updates the existing `TransitAgency` (created [previously](#configuration-for-development-and-testing)) with associations to the eligibility types, enrollment flows, and transit processor that were just created for testing.

At this point, Cal-ITP and transit agency staff can coordinate to do on-the-ground testing where a live card is tapped on a live payment validator.

### Production validation testing

1. Transit agency staff (or Cal-ITP staff) does live test in the field.
1. Transit agency staff uses the Merchant Portal to verify the taps and discounts were successful.
1. Cal-ITP uses logs from Azure to verify the user was associated to the customer group.
1. Cal-ITP verifies that Amplitude analytic events are being sent.

## Configuration for production

Once production validation is done, the transit agency can be added to the production Benefits database.

### Steps

1. Cal-ITP creates a customer group **for production use** in production Littlepay.
1. Cal-ITP associates the group with the discount product created [previously during production validation](#configuration-for-production-validation).
1. Cal-ITP sets that group's ID as the `group_id` for a new `EnrollmentFlow` in the Benefits database.
1. Cal-ITP configures the newly created `EnrollmentFlow` for the **production** eligibility verification system.
1. Cal-ITP creates a new `TransitAgency` in the database with proper associations to eligibility types, enrollment flows, and transit processor.

### Cleanup

At this point, the customer group that was created in production Littlepay for testing purposes can be deleted. The temporary production validation objects in the Benefits database can also be deleted.

1. Remove the association between the test customer group and discount product.
1. Delete the test customer group.
1. Remove temporary `EnrollmentFlow`s and `TransitProcessor` that were [created](#steps_1) in the Benefits test environment.
