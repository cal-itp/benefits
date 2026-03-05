# Configure an agency for production

Once production validation is done, the transit provider can be added to the production Benefits database.

=== "Littlepay"

    1.  Cal-ITP creates a customer group **for production use** in production Littlepay.
    1.  Cal-ITP associates the group with the discount product [created previously during production validation](#configuration-for-production-validation).
      - Once this is complete, verify that the setup is correct by using the [littlepay CLI](https://github.com/cal-itp/littlepay).
    1.  Cal-ITP creates a new `LittlepayGroup` in the Benefits prod environment:
      - Set the 'Group id' value to the corresponding **production** group ID.
      - The new `LittlepayGroup` is then associated with the correct enrollment flow and transit agency using the dropdowns.
    1.  Cal-ITP creates a new `LittlepayConfig` in the Benefits prod environment:
      - Set Environment to **Production**.
      - Choose the new `TransitAgency`.
      - Retrieve Audience and Client ID values for the **production** config from shared LastPass note.
      - [Create the client secret in the Azure Key Vault](../tutorials/secrets.md) for the prod environment, then paste its name in the Client Secret Name field.
      - Be sure to refresh the secrets for this to take effect!
         1.  In the Azure portal, go to the App Service.
         1.  Inside the App Service, navigate to Settings -> Environment variables.
         1.  Click the **Pull reference values** button to force the App Service to bypass the 24-hour cache and fetch the latest values for Key Vault references. This triggers a graceful restart of the app.
    1.  Cal-ITP returns to the `TransitAgency` instance and checks the **Active** box.

=== "Switchio"

    TK

At this point, real customers can begin enrolling their cards and receiving their discounted fares with this transit provider!

Next steps:

- [Post launch](./d-post-launch.md)
