# Configure a transit provider for production

Once production validation is done, the transit provider can be added to the production Benefits database.

_Typically performed by a Cal-ITP developer._

=== "Littlepay"

    1.  Cal-ITP creates a customer group **for production use** in production Littlepay.
    1.  Cal-ITP associates the group with the discount product [created previously during production validation](#configuration-for-production-validation).
      - Once this is complete, verify that the setup is correct by using the [littlepay CLI](https://github.com/cal-itp/littlepay).
    1.  Cal-ITP creates a new `LittlepayGroup` in the Benefits prod environment:
      - Set the 'Group id' value to the corresponding **production** group ID.
      - The new `LittlepayGroup` is then associated with the correct enrollment flow and transit provider using the dropdowns.
    1.  Cal-ITP creates a new `LittlepayConfig` in the Benefits prod environment:
      - Set Environment to **Production**.
      - Choose the new `TransitAgency`.
      - Retrieve Audience and Client ID values for the **production** config from shared LastPass note.
      - Client Secret Name: `${agency_slug}-payment-processor-client-secret`
      --8<-- "./inc/create-secret.md"
    1.  Cal-ITP returns to the `TransitAgency` instance and checks the **Active** box.

=== "Switchio"

    1. Cal-ITP creates a new `SwitchioConfig` in the Benefits production environment:
      - Environment: **Production**
      - Label: `${agency_short_name}`
      - Tokenization api key: from LastPass
      - Tokenization api secret name: `${agency_slug}-switchio-prod-api-secret`
      --8<-- "./inc/create-secret.md"
      - Enrollment api authorization header: See LastPass (same for all agencies in the env)
      - Pto id: from LastPass
      - Client certificate: Switchio (prod) client certificate (same for all agencies in the env)
      - Ca certificate: Switchio (prod) CA certificate (same for all agencies in the env)
      - Private key: Switchio (prod) private key (same for all agencies in the env)

    1. Cal-ITP creates a new `SwitchioGroup` in the Benefits test environment for each enrollment flow:
      - Group id: (unlike Littlepay, same for all agencies in the env)
    1. Cal-ITP returns to the `TransitAgency` instance and selects the `SwitchioConfig` above as the agency's transit processor config and checks the **Active** box.

At this point, real customers can begin enrolling their cards and receiving their discounted fares with this transit provider!

Next steps:

- [Transit provider post-launch](./d-post-launch.md)
