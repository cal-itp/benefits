# Getting started with manual testing

Manual testing is an important part of the feature release and refactoring processes. This testing can take on different forms
and is performed in different environments for given scenarios (see [When to test](#when-to-test) below).

In order to test a complete enrollment flow in the app in any environment but `production`, you will need to use appropriate
test credentials for the flow and associated identity provider(s) (IdPs).

The [Benefits Test Data document](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit?tab=t.0) has more information about the supported systems and test credentials for each.

## Login.gov

See the tutorial on [Using the Login.gov sandbox](../../tutorials/logingov-sandbox.md) to learn how to setup a Login.gov
sandbox account for testing. Note you can create _multiple_ Login.gov sandbox accounts for testing different scenarios
(Older Adult and U.S. Veteran for example).

## Agency cards

To test the agency card enrollment pathways, we primarily use sample credentials specific to the Transit Agency:

- [Agency Cards (CST)](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit?tab=t.0#heading=h.jxhxmhjl8rik)
- [Courtesy Cards (MST)](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit#heading=h.l2jcqsl4s6rh)
- [Reduced Fare Mobility ID (SBMTD)](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit#heading=h.rkuhoc19aku7)

## Payment cards

To test the Littlepay or Switchio card enrollment flows, use sample [Payment card information](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit#heading=h.6l8f6lihq1vz), along with any fake name, any CVV and an expiration date in the future.

## Benefits Administrator

To test the Benefits Administrator from the perspective of a _Transit Agency user_, sign in using the sample [Benefits Admin account](https://docs.google.com/document/d/1bFynuiLy9POXYEYnLVEQJpAm1TVqlappN9lU9ev3Bvg/edit?tab=t.0#heading=h.yavvkfyg4n).

## When to test

The following table outlines some key conditions in which different manual testing scenarios should be run.

| Condition                                                            | Scenario(s)                                           | Environment(s)         |
| -------------------------------------------------------------------- | ----------------------------------------------------- | ---------------------- |
| New feature development                                              | [in-person][ip], [self-service][ss]                   | `local`, `dev`         |
| Bug fixes, refactors, etc. that do not change expected functionality | [in-person][ip], [self-service][ss]                   | `local`, `dev`         |
| New or refactored designs, layouts, fonts, colors, etc.              | [keyboard][kb]                                        | `local`, `dev`, `test` |
| New translations and/or updated copy                                 | [translations][tr]                                    | `local`, `test`        |
| New agency onboarding                                                | [in-person][ip], [self-service][ss], translations[tr] | `test`                 |
| Deployment to `test`                                                 | [in-person][ip], [self-service][ss]                   | `test`                 |
| Release to `prod`                                                    | [smoke testing][sk]                                   | `prod`                 |

[ip]: ./in-person.md
[kb]: ./keyboard.md
[sk]: ./smoke-testing.md
[ss]: ./self-service.md
[tr]: ./translations.md
