# Seniors

One Benefits application use case is for riders age 65 years and older. The Benefits application verifies the person's age to confirm eligibility and allows those eligible to enroll their contactless payment card for their transit benefit.

Currently, the app uses [Login.gov's Identity Assurance Level 2 (IAL2)](https://developers.login.gov/attributes/) to confirm age, which requires a person to have a Social Security number, a valid state-issued ID card and a phone number with a phone plan associated with the person's name. Adding ways to confirm eligibility for people without a Social Security number, for people who are part of a transit agency benefit program are on the roadmap.

## Demonstration

Here's a GIF showing what the flow looks like, having seniors confirm eligibility via Login.gov and enroll via LittlePay:

![Demonstration of the sign-up process for a senior confirming eligibility via Login.gov and enrolling via Littlepay](img/senior-success.gif){ width="350" }

## Process

```mermaid
sequenceDiagram
    actor Rider
    participant Benefits as Benefits app
    participant IdG as Identity Gateway
    participant Login.gov
    participant Littlepay

    Rider->>Benefits: visits site
    Benefits-->>IdG: identity proofing
    IdG-->>Login.gov: identity proofing
    Rider->>Login.gov: enters SSN and ID
    Login.gov-->>IdG: eligibility verification
    IdG-->>Benefits: eligibility verification
    Benefits-->>Littlepay: enrollment start
    Rider->>Littlepay: enters payment card details
    Littlepay-->>Benefits: enrollment complete
```
