# Enrollment

Enrollment is the core workflow in Cal-ITP Benefits. It’s the process that eligible riders complete to automatically receive reduced fares when they tap to pay for transit with their debit or credit card. A transit benefit enrollment consists of three primary, sequential steps.

```mermaid
%% The key steps in an enrollment in Cal-ITP Benefits
graph LR
    subgraph Transit benefit enrollment
        direction LR
        A[Identity <br>confirmation] --> B[Eligibility<br>verification] --> C[Card<br>registration]
    end
    style A fill:#f9e27f,stroke:#c8b045,color:#000
    style B fill:#7fb3e0,stroke:#4a8abf,color:#000
    style C fill:#a8d5a2,stroke:#6aab62,color:#000
```

## Supported enrollment pathways

Cal-ITP Benefits offers the following enrollment pathways to all transit providers as part of the standard product offering.

| Enrollment pathway                              | Self-service eligibility verifier                                                     | Status  | Launch               | Available for in-person enrollment |
| ----------------------------------------------- | ------------------------------------------------------------------------------------- | ------- | -------------------- | ---------------------------------- |
| [**Older adults**][older-adults]                | [Login.gov ID Proofed](https://developers.login.gov/attributes/)                      | Live    | [08/2022][2022.08.1] | ✅                                 |
| [**Veterans**][veterans]                        | [Veteran Confirmation API](https://developer.va.gov/explore/api/veteran-confirmation) | Live    | [09/2023][2023.09.1] | ―                                  |
| [**Low-income**][low-income]                    | CalFresh Confirm API                                                                  | Live    | [07/2024][2024.07.1] | ―                                  |
| [**Medicare cardholders**][medicare]            | [Blue Button API](https://bluebutton.cms.gov/developers/#overview)                    | Live    | [09/2024][2024.09.3] | ✅                                 |
| [**Veterans with disabilities**][disabled vets] | [Veteran Service History and Eligibility API][VA VSHE API]                            | Planned | \*                   | \*                                 |

## Enrollment methods

Cal-ITP Benefits offers two different methods for a rider to enroll for a transit benefit: self-service and in-person enrollment.

### Self-service enrollment

Self-service enrollment allows riders to complete enrollment by visiting the web application available at [benefits.calitp.org](https://benefits.calitp.org) on their desktop or mobile device at a time and place that is convenient for them. The vast majority of riders choose this enrollment method for its convenience and privacy-forward approach. Transit providers prefer it as well, as it reduces the operational time that agency staff spend on administering their discount fare program.

#### Identity confirmation and eligibility verification

The vast majority of self-service enrollments in Cal-ITP Benefits are facilitated by the California Department of Technology Identity Gateway. The app handles identity confirmation for self-service enrollments using Login.gov, a federal digital identity provider. Riders not only need a Login.gov account but must also allow complete identity proofing in Login.gov.

Once the Identity Gateway successfully identifies a person, it then verifies their eligibility for a transit benefit through a variety of data-sharing agreements with state and federal partners, depending on the benefit option a user chooses. See the table below for details

There are currently four self-service enrollment pathways that transit operators can offer their riders in Cal-ITP Benefits. Follow the links below for additional details about each pathway.

- [Older adults][older-adults]
- [Medicare cardholders][medicare]
- [U.S. Veterans][veterans]
- [CalFresh cardholders][low-income]

!!! note

    During the pilot phase of Cal-ITP Benefits, we offered our early adopters, MST and SBMTD, an [agency cardholder enrollment pathway][agency-cards]. While these enrollments pathways are still in active use for those agencies, we no longer offer self-service enrollment for agency cardholders as base functionality in the product. Implementing this benefit option requires extensive collaboration between the agency’s IT staff and Cal-ITP engineers. Going forward, Cal-ITP is devoting its collective effort to expanding self-service enrollment options so that the agency cardholder enrollment option is no longer necessary. We anticipate eventually sunsetting agency cardholder enrollment entirely.

#### Card registration

Once an eligible rider completes the identity check and confirms their eligibility for a transit benefit, Cal-ITP Benefits connects them to the agency’s transit processor so they can register their debit or credit card for reduced fares. An agency contracts with a single transit processor. Cal-ITP Benefits is currently integrated with two transit processors.

- [Littlepay][littlepay]
- [Switchio][switchio]

#### Configuration

All self-service enrollment pathways are disabled by default; each transit operator chooses the set of benefit options they want to offer their riders. Cal-ITP Account Managers can enable or disable self-service enrollment pathways at any time in the transit agency configuration in Cal-ITP Benefits Administrator. If a transit operator launches with—for example— the Older adult and Medicare cardholder benefit options, they can subsequently elect to offer Veterans or people with low income the option to enroll as well at any time after launching the service. Once enabled, the enrollment pathway is immediately available in the menu of benefit options for riders.

!!! note

    For transit operators that have elected to join a region, all operators in the region must offer the same benefits options for self-service enrollment.

### In-person enrollment

In-person enrollment allows riders to complete enrollment by visiting an agency location or planned event to work with an agency staff member using _Cal-ITP Benefits Administrator_ available at [benefits.calitp.org/admin](benefits.calitp.org/admin). Less than 10% of enrollments are processed in Cal-ITP Benefits using this method, but it is an important complement to self-service enrollment when agencies prefer to offer “high-touch” customer service for certain riders, when riders struggle with the technology required for self-service verification, or for certain use cases that don’t allow eligible riders to utilize self-service enrollment. Additionally, it is an important “fallback” method for agencies to continue processing enrollments when self-service enrollment is unavailable due to technical issues.

#### Identity confirmation and eligibility verification

The key difference between in-person enrollment and self-service enrollment is that the agency staff member completes the eligibility verification using a government-issued photo ID and any other required documents while the rider is physically present in the same space.

#### Card registration

Riders register their cards during an in-person enrollment the same way they do during a self-service enrollment, except that the form for them to input card details is presented in Cal-ITP Benefits Administrator rather than in the rider-facing application at benefits.calitp.org.

#### Configuration

There are currently three in-person enrollment pathways that transit operators can offer their riders in Cal-ITP Benefits. Any time a self-service enrollment pathway is available to riders, the corresponding in-person enrollment pathway will also be enabled. It certain configurations, it is possible that in-person enrollment options will be enabled without a corresponding self-service enrollment option.

Follow the links below for additional details about each pathway.

- [Older adults][older-adults]
- [Medicare cardholders][medicare]
- [Agency cardholders][agency-cards]

!!! note

    While we no longer offer [agency cardholder enrollment][agency-cards] as a _self-service_ option, we do support it for in-person enrollment.

[older-adults]: enrollment-pathways/older-adults.md
[agency-cards]: enrollment-pathways/agency-cards.md
[veterans]: enrollment-pathways/veterans.md
[medicare]: enrollment-pathways/medicare-cardholders.md
[low-income]: explanation/enrollment-pathways/low-income.md
[littlepay]: https://littlepay.com/
[switchio]: https://switchio.com/transport/
[2022.08.1]: https://github.com/cal-itp/benefits/releases/tag/2022.08.1
[2022.11.1]: https://github.com/cal-itp/benefits/releases/tag/2022.11.1
[2023.09.1]: https://github.com/cal-itp/benefits/releases/tag/2023.09.1
[2024.07.1]: https://github.com/cal-itp/benefits/releases/tag/2024.07.1
[2024.09.3]: https://github.com/cal-itp/benefits/releases/tag/2024.09.3
[disabled vets]: https://github.com/cal-itp/benefits/issues/3048
[VA VSHE API]: https://developer.va.gov/explore/api/veteran-service-history-and-eligibility/docs?version=current
