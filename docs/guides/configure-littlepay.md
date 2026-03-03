# Configure Littlepay for a transit agency

## Configuration for development and testing

For development and testing, only a Littlepay customer group is needed since there is no need to interact with any discount product. (We don't have a way to tap a card against the QA system to trigger a discount and therefore have no reason to associate the group with any product.)

This work can begin once the transit provider has a contract in place with Littlepay.

- Cal-ITP uses the transit provider's Littlepay merchant ID to create a customer group in the Littlepay QA environment for each type of eligibility (e.g. older adult).
  - _Typically performed by transit provider's Account Manager_
  - For each group that is created, a group ID will be returned and should be set as the `group_id` on a new `LittlepayGroup`.
  - The new `LittlepayGroup` is then associated with an enrollment flow and transit agency using the dropdowns. (See [Configuration data](../tutorials/load-sample-data.md) for more on loading the database.)
- Cal-ITP requests and receives Littlepay Back Office API access (for both PROD and QA) for the new transit provider.
  - _Typically requested by a developer via email to Littlepay_

## Configuration for production validation

**Production validation** is the process of doing an end-to-end test of enrolling a real person's card through the Benefits app and using it to ride with a discounted fare. The word "production" here refers to **Littlepay's production environment** (which must be used to take a ride in real life), but the Benefits application's test environment is used for the enrollment process to avoid disruption of the Benefits production environment.

For production validation, both customer groups and a discount product are needed.

1. Transit provider staff creates the discount product in production Littlepay (if it does not already exist).
1. Transit provider staff takes a screenshot of the discount product in the Merchant Portal, making sure the browser URL is visible, and sends that to Cal-ITP.
1. Cal-ITP creates the customer groups in production Littlepay.
1. Cal-ITP associates the groups with the product.
   - _Typically performed by transit provider's Account Manager_
   - Once this is complete, verify that the setup is correct by using the [littlepay CLI](https://github.com/cal-itp/littlepay). Example:

   ```bash
   $ littlepay groups products
   👥 Matching groups (3): ⚠️  prod, edcta
   GroupResponse(id='b9634346-5a03-448d-8f7a-c7bec1169e00', label='Discounted', participant_id='eldorado-transit')
     🛒 Linked products (1)
     ProductResponse(id='56755aa9-0227-4208-a8a4-8b3217cebaa9', code='Daily Max - Discounted', status='ACTIVE', type='CAPPING', description='Daily Max - Discounted', participant_id='eldorado-transit')
   GroupResponse(id='f410db55-f1b5-49ef-8072-a5bbb685d0f5', label='Medicare', participant_id='eldorado-transit')
     🛒 Linked products (2)
     ProductResponse(id='b9f4b2aa-ecc2-4019-9552-03d7af4c484c', code='Medicare', status='ACTIVE', type='CAPPING', description='Medicare', participant_id='eldorado-transit')
     ProductResponse(id='05b43044-759d-4938-b150-2adc603e4f74', code='Medicare', status='ACTIVE', type='DISCOUNT', description='Medicare', participant_id='eldorado-transit')
   GroupResponse(id='e88042e2-7b56-4ffa-83b6-fa895a8e6a3d', label='Senior 65+', participant_id='eldorado-transit')
     🛒 Linked products (2)
     ProductResponse(id='267edc99-6989-4779-a445-94a121387a25', code='Senior 65+', status='ACTIVE', type='DISCOUNT', description='Senior 65+', participant_id='eldorado-transit')
     ProductResponse(id='d7d948c2-20bf-4b10-a181-d1f2c89456b6', code='Senior 65+', status='ACTIVE', type='CAPPING', description='Senior 65+', participant_id='eldorado-transit')
   ```

1. Cal-ITP creates a new `LittlepayGroup` in the Benefits test environment:
   - Set the 'Group id' to the corresponding **production** group ID (from production Littlepay) for production validation.
     - This will be set back to the QA group value after final production configuration is complete.
   - The new `LittlepayGroup` is then associated with the correct enrollment flow and transit agency using the dropdowns.
1. Cal-ITP creates a new `LittlepayConfig` in the Benefits test environment:
   - Set Environment to **Testing** for production validation.
     - This will be set back to QA after final production configuration is complete.
   - Choose the new `TransitAgency`.
   - Retrieve Audience and Client ID values for the **production** config from shared LastPass note.
   - [Create the client secret in the Azure Key Vault](../tutorials/secrets.md) for the test environment, then paste its name in the Client Secret Name field.
     - Be sure to refresh the secrets for this to take effect!
       1. In the Azure portal, go to the App Service.
       1. Inside the App Service, navigate to Settings -> Environment variables.
       1. Click the **Pull reference values** button to force the App Service to bypass the 24-hour cache and fetch the latest values for Key Vault references. This triggers a graceful restart of the app.
1. Cal-ITP returns to the `TransitAgency` instance and selects the `LittlepayConfig` above as the agency's transit processor config and checks the **Active** box.

At this point, Cal-ITP and transit provider staff can coordinate to do on-the-ground testing using the [test client](https://test-benefits.calitp.org) to enroll a real card and testing it by tapping on a live payment validator.

### Production validation testing

1. Transit provider staff (or Cal-ITP staff) does live test in the field.
1. Transit provider staff uses the Merchant Portal to verify the taps and discounts were successful.
1. Cal-ITP uses logs from Azure to verify the user was associated to the customer group.
1. Cal-ITP verifies that Amplitude analytic events are being sent.

## Configuration for production

Once production validation is done, the transit provider can be added to the production Benefits database.

1. Cal-ITP creates a customer group **for production use** in production Littlepay.
1. Cal-ITP associates the group with the discount product [created previously during production validation](#configuration-for-production-validation).
   - Once this is complete, verify that the setup is correct by using the [littlepay CLI](https://github.com/cal-itp/littlepay).

1. Cal-ITP creates a new `LittlepayGroup` in the Benefits prod environment:
   - Set the 'Group id' value to the corresponding **production** group ID.
   - The new `LittlepayGroup` is then associated with the correct enrollment flow and transit agency using the dropdowns.
1. Cal-ITP creates a new `LittlepayConfig` in the Benefits prod environment:
   - Set Environment to **Production**.
   - Choose the new `TransitAgency`.
   - Retrieve Audience and Client ID values for the **production** config from shared LastPass note.
   - [Create the client secret in the Azure Key Vault](../tutorials/secrets.md) for the prod environment, then paste its name in the Client Secret Name field.
     - Be sure to refresh the secrets for this to take effect!
       1. In the Azure portal, go to the App Service.
       1. Inside the App Service, navigate to Settings -> Environment variables.
       1. Click the **Pull reference values** button to force the App Service to bypass the 24-hour cache and fetch the latest values for Key Vault references. This triggers a graceful restart of the app.
1. Cal-ITP returns to the `TransitAgency` instance and checks the **Active** box.

At this point, real customers can begin enrolling their cards and receiving their discounted fares with this transit provider!

--8<-- "inc/verify-enrollments.md"

## Cleanup

Once the transit provider is live in production, there are some cleanup steps to take.

_These items can all be done in parallel, and can also be done in parallel with the analytics verification described above._

### Update transit provider configuration in test environment

The transit provider's configuration in the test environment should be updated to change the production values back to the QA values for its steady state going forward.

- Littlepay config
  - Environment
  - Audience
  - Client ID
  - Client secret [(update value in Azure Key Vault)](../tutorials/secrets.md)
- Littlepay groups:
  - Set group IDs back to the groups [created previously during development and testing configuration](#configuration-for-development-and-testing)
  - Once this is complete, verify that the setup is correct by using the [littlepay CLI](https://github.com/cal-itp/littlepay).
