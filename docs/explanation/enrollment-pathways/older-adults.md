# Older adults

One Benefits application use case is for riders age 65 years and older. The Benefits application verifies the person's age to confirm eligibility and allows those eligible to enroll their contactless payment card for their transit benefit.

Currently, the app uses [Login.gov's Identity Assurance Level 2 (IAL2)](https://developers.login.gov/attributes/) to confirm age, which requires a person to have a Social Security number, a valid state-issued ID card and a phone number with a phone plan associated with the person's name. Adding ways to confirm eligibility for people without a Social Security number, for people who are part of a transit agency benefit program are on the roadmap.

## Demonstration

Here's a video walkthrough of the rider self-service enrollment experience when choosing the Older adult enrollment pathway.

<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/vAJ_3lTeWJU?si=FCQX51zX_aaL556_&amp;controls=0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## Self-service enrollment

```mermaid
sequenceDiagram
autonumber
%% Self-service Enrollment for Older Adults
    actor TransitRider as Transit Rider
    participant Benefits as Cal-ITP Benefits
    participant IdG as Identity Gateway
    participant verifyIdentity as Login.gov
    participant TransitProcessor as Transit processor
TransitRider->>Benefits: visits benefits.calitp.org
    activate Benefits
Benefits-->>IdG: begins identity verification
    activate IdG
TransitRider->>verifyIdentity: account authentication
    activate verifyIdentity
    Note over verifyIdentity: Authenticated (Y/N)
verifyIdentity-->>IdG: identity confirmation
IdG-->>verifyIdentity: requests required PII
    Note over verifyIdentity: Date of Birth
verifyIdentity-->>IdG: returns response
    deactivate verifyIdentity
    Note over IdG: Age 65 or older (Y/N)
IdG-->>Benefits: eligibility response
    deactivate IdG
Benefits-->>TransitProcessor: card registration start
    activate TransitProcessor
TransitRider->>TransitProcessor: provides debit or credit card details
TransitProcessor-->>Benefits: card registration confirmation
    deactivate TransitProcessor
    deactivate Benefits
    Note over Benefits: Successfull enrollment
```
