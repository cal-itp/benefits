# Configure for production validation

**Production validation** is the process of doing an end-to-end test of enrolling a real person's card through the Benefits app and using it to ride with a discounted fare. The word "production" here refers to **Littlepay's production environment** (which must be used to take a ride in real life), but the Benefits application's test environment is used for the enrollment process to avoid disruption of the Benefits production environment.

_Typically performed by a Cal-ITP developer._

=== "Littlepay"

    For production validation, both customer groups and a discount product are needed.

    1. Transit provider staff creates the discount product and associated customer groups in production Littlepay.
    1. Transit provider provides group names and ids and Cal-ITP verifies that the setup is correct by using the [Littlepay CLI](https://github.com/cal-itp/littlepay). Example:

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
      - The new `LittlepayGroup` is then associated with the correct enrollment flow and transit provider using the dropdowns.
    1.  Cal-ITP [creates a `TransitAgency`](./add-transit-provider.md#add-the-transit-provider-to-the-application) in the test environment
    1. Cal-ITP creates a new `LittlepayConfig` in the Benefits test environment:
      - Set Environment to **Production** for production validation.
        - This will be set back to **Testing** after final production configuration is complete.
      - return to the `TransitAgency` and associate the new `LittlepayConfig` as its 'Transit processor config'.
      - Retrieve Audience and Client ID values for the **production** config from shared LastPass note.
      - Client Secret Name: `${agency_slug}-payment-processor-client-secret`
      --8<-- "./inc/create-secret.md"
    1. Cal-ITP returns to the `TransitAgency` instance and selects the `LittlepayConfig` above as the agency's transit processor config and checks the **Active** box.

=== "Switchio"

    1.  Cal-ITP [creates a `TransitAgency`](./add-transit-provider.md#add-the-transit-provider-to-the-application) in the test environment
    1. Cal-ITP creates a new `SwitchioConfig` in the Benefits test environment:
      - Environment: **Testing**
      - Label: `${agency_short_name}`
      - Tokenization api key: from LastPass
      - Tokenization api secret name: `${agency_slug}-switchio-acc-api-secret`
      --8<-- "./inc/create-secret.md"
      - Enrollment api authorization header: See LastPass (same for all agencies in the env)
      - Pto id: from LastPass
      - Client certificate: Switchio (ACC) client certificate (same for all agencies in the env)
      - Ca certificate: Switchio (ACC) CA certificate (same for all agencies in the env)
      - Private key: Switchio (ACC) private key (same for all agencies in the env)

    1. Cal-ITP creates a new `SwitchioGroup` in the Benefits test environment for each enrollment flow:
      - Group id: (unlike Littlepay, same for all agencies in the env)
    1. Cal-ITP returns to the `TransitAgency` instance and selects the `SwitchioConfig` above as the agency's transit processor config and checks the **Active** box.

At this point, Cal-ITP and transit provider staff can coordinate to do on-the-ground testing using the [test client](https://test-benefits.calitp.org) to enroll a real card and test it by tapping on a live payment validator.

### Production validation testing

1. Transit provider staff (or Cal-ITP staff) does live test in the field.
1. Transit provider staff verify the taps and confirm that discounts were applied.
1. Cal-ITP uses logs from Azure to verify the user was associated to the customer group.
1. Cal-ITP verifies that Amplitude analytic events are being sent.

Next steps:

- [Configure for production](./configure-production.md)
- [Post-launch](./post-launch.md)
