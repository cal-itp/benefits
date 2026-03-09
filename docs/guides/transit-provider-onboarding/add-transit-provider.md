# Add a new transit provider

This set of guides describe the steps needed to add a new transit provider to the application and take them from testing to production.

Before starting any configuration, the Cal-ITP team and transit provider staff should have a kickoff meeting to confirm that information provided is complete, implementation plan is feasible, and any approvals needed have been obtained.

Then, the Cal-ITP team completes the steps below to configure the new transit provider in the Benefits application.

_These items can all be done in parallel._

## Create transit provider onboarding epic

_Typically performed by the Benefits Product Manager._

1. Navigate to the [Cal-ITP Benefits repository, Actions tab](https://github.com/cal-itp/benefits/actions)
2. Look in the left bar for the (pinned) workflow called `Agency Onboarding Issue Scaffold`, click on this to open the workflow run history
3. In the center view, on the top right, look for a drop-down button that says `Run workflow`, and click this
4. Leaving the branch selection the default (`main`), provide values for the other inputs (some of which are required)
   - For the `Estimated launch date`, enter a value like `August 2026`
   - For the `Initiative issue`, enter the number only like `1234`
5. Click the green `Run workflow` button under the input fields
6. Refresh the current page to see an in-progress workflow run, wait for it to finish with a green checkmark

Once the workflow runs successfully, the onboarding epic and all sub-issues will have been created based on the input data provided. They can be further edited, modified from the USB, etc. as normal.

## Add transit provider to adoption table

_Typically performed by the Benefits Product Manager._

The workflow above will also open a Pull Request that adds the new transit provider to the adoption table in the README, similar to this [example](https://github.com/cal-itp/benefits/pull/2944). It can be further modified as needed.

## Produce a properly formatted transit provider logo

_Typically performed by a designer._

The application currently requires one transit provider logo for display on the landing page. The logo should be white with a clear background in the dimensions below:

- height: 64px
- width: any

## Add the transit provider to the application

_Typically performed by a Cal-ITP developer._

The steps below are the same whether you are adding the agency to our dev, test or production environment.

- Add a new transit provider in the Admin with the following:
  - Slug: Define the agency's unique landing page (no spaces or special characters)
  - Short name, long name, info URL, phone, enrollment flows and supported card schemes: Get from their enrollment form
  - Logo: Typically found attached to a GitHub issue comment
  - Transit processor config: leave blank for now
  - Active: Leave **unchecked** for now

The steps to create a transit processor config and associate it with your new agency are specific to the payment processor they contract with.

## Configure for development and testing

=== "Littlepay"

    For development and testing, only a Littlepay customer group is needed since there is no need to interact with any discount product. (We don't have a way to tap a card against the QA system to trigger a discount and therefore have no reason to associate the group with any product.)

    This work can begin once the transit provider has a contract in place with Littlepay.

    - Transit provider uses the Littlepay Merchant Portal to create a customer group in the Littlepay QA environment for each type of eligibility (e.g. older adult).
      - _Typically performed by transit provider's Account Manager_
      - For each group that was created, a group ID will be returned and should be set as the `group_id` on a new `LittlepayGroup`.
    - Cal-ITP requests and receives Littlepay Back Office API access (for both PROD and QA) for the new transit provider.
      - _Typically requested by a developer via email to Littlepay_

=== "Switchio"

    For development and testing, the agency can use the same INT credentials as CST (stored in LastPass).
    - Switchio API credentials are typically requested by a Cal-ITP developer in Slack.
    - A `SwitchioGroup` is created in admin for each enrollment flow using identifiers common to other agencies.

Next steps:

- [Configure for production validation](./configure-production-validation.md)
- [Configure for production](./configure-production.md)
