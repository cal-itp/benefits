# Using the Login.gov sandbox

To test an enrollment flow that utilizes Login.gov as the Identity Provider (IdP), you will need an account in the
[Login.gov sandbox](https://developers.login.gov/testing/):

> The Login.gov sandbox is an open environment to create and test integrations between Login.gov and your applications

This tutorial walks you through the process of setting up a Login.gov sandbox account that can be used for testing the Benefits
app.

!!! abstract "You will need"

    To create a full identity-proofed Login.gov sandbox account, you will need:

    - a real email address that can receive email
    - a real cell phone number that can receive an SMS
    - a specially formatted test account `YAML` file (see [more below](#test-account-yaml-files))

Read [the Login.gov Testing identity proofing](https://developers.login.gov/testing/#testing-identity-proofing) docs for
complete details.

## Test account `YAML` files

The specially formatted `YAML` files are used in place of a state ID document upload during the Login.gov sandbox account
identity proofing flow. The Login.gov sandbox will use information from an uploaded `YAML` file in place of the real identity
verification required for Production Login.gov.

The [Benefits Test Data document](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit#heading=h.t61g222qmr19) links to a few pre-made `YAML` files that can be used for various scenarios:

- Older Adult
- U.S. Veteran
- CalFresh recipient

Login.gov also provides more information and sample `YAML` files in their [Testing document upload for Basic IdV Service](https://developers.login.gov/testing/#testing-document-upload-for-the-basic-idv-service-without-facial-matching) docs.

## Create a basic account

1. Navigate to the [Login.gov sandbox account creation page](https://idp.int.identitysandbox.gov/sign_up/enter_email)
1. Enter a unique email address for this test case, e.g. `realemail+older_adult@provider.com`. [Gmail supports adding suffixes to your email address](https://support.google.com/a/users/answer/9282734?visit_id=638381024326725285-629188737&rd=1#email-address-variation).
1. Select a language and check **I read and accept the Login.gov Rules of Use** and submit.
1. Check your email for a confirmation link and click it.
1. Create a strong, unique password for use with this test account only. **Save this (ideally with a password manager)**.
1. Continue to setup a multi-factor authentication method. Selecting _Backup codes_ is perfectly fine especially if this is a temporary test account, but note that you only get 10 one-time-use codes. You will get a fresh 10 after using the first batch. _Authentication application_ or **Text or voice message** may be better options if you plan to use the test account frequently, for some time.

At this point, you will be shown your Login.gov sandbox account page, and you are signed in.

You now have a (non identity proofed) Login.gov sandbox account.

!!! tip "Try it!"

    Sign out of your Login.gov sandbox account. Then sign back from the same screen.

    Are you able to get back to the account page?

## Upgrade basic account to identity proofed

The basic sandbox account does not have enough details to allow for eligibility checks with the Benefits app
(like date of birth, address, etc.)

The easiest way to upgrade the sandbox account is to attempt to use it for a particular enrollment flow in the Benefits app.

This process will prompt you through the identity proofing flow before taking you back to the Benefits app.

1. Download or create the `YAML` file for the specific user-type you are testing (Older Adult, U.S. Veteran, etc.)
   - The information in the `YAML` file should be _sample information only_.
   - The information in the `YAML` file _does not_ need to match later information you will provide in the flow (e.g. phone number)
1. Start in a non-`prod` environment of the Benefits app (e.g. `dev` or `test`).
1. Select a transit agency, and select the Login.gov flow corresponding to the user-type you are testing.
1. Sign in to Login.gov sandbox using the basic account details you set up previously.
1. Continue through the confirmation screens that outline the identity proofing process.
1. On the **Choose how to verify your ID** page, select **Upload photos** under _Continue on this computer_.
1. On the **Choose your ID type** page, select **U.S. driver's license or state ID** and continue.
1. Upload the `YAML` file as the _Front_ and _Back_ image of the ID and submit.
1. Enter a **fake** Social Security number following the on-screen instructions (must start with `900-` or `666-`). _DO NOT enter real PII in this field_.
1. Verify the (sample) information was processed from the `YAML` file and submit.
1. Enter your real cell phone number to receive a verification SMS.
1. Check your text messages for a message from Login.gov. The message should specify `idp.int.identitysandbox.gov`.
1. Enter the code into the browser.
1. Re-enter your Login.gov sandbox account password.
1. Save the displayed **Personal Key** somewhere safe (this can be used for account recovery).
1. Confirm that you want to connect the verified information in your Login.gov sandbox account to the Benefits app.

At this point, you will be redirected back into the Benefits app.

If the Login.gov sandbox account was created with sample data sufficient to pass eligibility for the chosen enrollment flow
(e.g. a date of birth making the sandbox account 65 or older for the Older Adult flow), you are shown the
"eligibility verified" message and can continue with contactless card enrollment.

!!! success "Success!"

    You now have an identity proofed Login.gov sandbox account that can be used for future testing.
