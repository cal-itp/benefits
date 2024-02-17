# Older adults

One Benefits application use case is for riders age 65 years and older. The Benefits application verifies the person's age to confirm eligibility and allows those eligible to enroll their contactless payment card for their transit benefit.

Currently, the app uses [Login.gov's Identity Assurance Level 2 (IAL2)](https://developers.login.gov/attributes/) to confirm age, which requires a person to have a Social Security number, a valid state-issued ID card and a phone number with a phone plan associated with the person's name. Adding ways to confirm eligibility for people without a Social Security number, for people who are part of a transit agency benefit program are on the roadmap.

## Demonstration

The video walkthough below demonstrates the flow for an older adult who has a Login.gov account to confirm transit benefit eligibility and enroll their bank card for reduced fares via LittlePay:

https://github.com/cal-itp/benefits/assets/6279581/139c77fa-ac75-4189-8b20-61d91051b264

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
