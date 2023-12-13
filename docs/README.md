# Project overview

This website provides technical documentation for the [`benefits`][benefits-repo] application from the
[California Integrated Travel Project (Cal-ITP)][calitp].

Documentation for the `dev` (default) branch is available online at: <https://docs.calitp.org/benefits>.

## Overview

Cal-ITP Benefits is an application that enables automated eligibility verification and enrollment for transit
benefits onto customers' existing contactless bank (credit/debit) cards.

The development of this publicly-accessible client is being managed by Caltrans' California Integrated Travel Project (Cal-ITP), in partnership with the California Department of Technology (CDT). From the [Cal-ITP site](https://www.calitp.org/):

> Our Cal-ITP Benefits web application streamlines the process for transit riders to instantly qualify for and receive discounts, starting with Monterey-Salinas Transit (MST), which offers a half-price Senior Fare. Now older adults (65+) who are able to electronically verify their identity are able to access MST's reduced fares without the hassle of paperwork.
>
> We worked with state partners on this product launch, and next we're working to bring youth, lower-income riders, veterans, people with disabilities, and others the same instant access to free or reduced fares across all California transit providers, without having to prove eligibility to each agency.

The application is accessible to the public at [benefits.calitp.org](https://benefits.calitp.org).

### Adoption by transit agencies

The following California transit agencies have launched Cal-ITP Benefits for their riders, with the following enrollment pathway options:

| Transit agency                                  | Older adults | Agency card | Veterans | Initial agency launch |
| ----------------------------------------------- | ------------ | ----------- | -------- | --------------------- |
| **Monterey-Salinas Transit**                    | Live         | Live        | Live     | 5/2021                |
| **Santa Barbara Metropolitan Transit District** | Live         | In test     |          | 10/2023               |
| **Sacramento Regional Transit District**        | In test      |             |          |                       |

### Supported enrollment pathways

The Cal-ITP Benefits app supports the following enrollment pathways that use the corresponding eligibility verification methods:

| Enrollment pathway                                             | Eligibility verification                                                              | Status | Launch                                                                |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------- |
| [**Older adults**](/benefits/enrollment-pathways/older-adults) | [Login.gov IAL2](https://developers.login.gov/attributes/)                            | Live   | [8/2022](https://github.com/cal-itp/benefits/releases/tag/2022.08.1)  |
| [**Agency cards**](/benefits/enrollment-pathways/agency-cards) | [Eligibility API](https://docs.calitp.org/eligibility-api/specification/)             | Live   | [11/2022](https://github.com/cal-itp/benefits/releases/tag/2022.11.1) |
| [**Veterans**](/benefits/enrollment-pathways/veterans)         | [Veteran Confirmation API](https://developer.va.gov/explore/api/veteran-confirmation) | Live   | [9/2023](https://github.com/cal-itp/benefits/releases/tag/2023.09.1)  |

Read more about each [enrollment pathway](/benefits/enrollment-pathways/).

## Technical details

`benefits` is a [Django 4][django] web application. The application talks to one or more [Eligibility Verification APIs](https://docs.calitp.org/eligibility-api/specification) or authentication providers. These APIs and the application are
designed for privacy and security of user information:

- The API communicates with signed and encrypted JSON Web Tokens containing only the most necessary of user data for the purpose of eligibility verification
- The application requires no user accounts and stores no information about the user
- Interaction with the application is anonymous, with only minimal event tracking for usage and problem analysis

Running the application locally is possible with [Docker and Docker Compose][docker]. [Hosting information.][hosting]

The user interface and content is available in both English and Spanish. Additional language support is possible via Django's
[i18n and l10n features][i18n].

The application communicates with external services like [Littlepay][littlepay] via API calls and others like the [Identity Gateway](https://dev.auth.cdt.ca.gov) via redirects, both over the public internet. See [all the system interconnections][interconnections].

## Security

Cal-ITP takes security and privacy seriously. Below is an overview of how the system is designed with security in mind.

### Architecture

The Benefits application is deployed to Microsoft Azure. Traffic is encrypted between the user and the application, as well as between the application and external systems.

The network is managed by the [California Department of Technology (CDT)](https://cdt.ca.gov/), who provide a firewall and [distributed denial-of-service (DDoS)](https://www.cloudflare.com/learning/ddos/what-is-a-ddos-attack/) protection.

You can find more technical details on [our infrastructure page](deployment/infrastructure/).

### Data storage

The Benefits application doesn't collect or store any user data directly, and we minimize the information exchanged between systems. The following information is temporarily stored in an encrypted session in the user's browser:

- The user's progress
- Credentials for interacting with the eligibility verification services

Sensitive user information exists in the following places:

- To enroll in a senior discount, users need to [provide personal information to Login.gov](https://benefits.calitp.org/help#login-gov-verify).
- Users need to [provide their credit or debit card information to our payment processor (Littlepay)](https://benefits.calitp.org/help#littlepay) to enroll in a discount.

None of that information is accessible to the Benefits system/team.

Learn more about the security/privacy practices of some of our third-party integrations:

- [Amplitude](https://amplitude.com/amplitude-security-and-privacy)
- [Littlepay](https://littlepay.com/privacy-policy/)
- [Login.gov](https://www.login.gov/policy/)

Benefits collects analytics on usage, without any identifying information. ([IP addresses are filtered out.](https://github.com/cal-itp/benefits/blob/3a5f7c28036b77355d7a137df4f33bd2a9362de1/benefits/core/templates/core/includes/analytics.html#L31))

### Practices

[Dependabot](https://github.com/features/security/software-supply-chain) immediately notifies the team of vulnerabilities in application dependencies.

Upon doing new major integrations, features, or architectural changes, the Benefits team has a penetration test performed by a third party to ensure the security of the system.

All code changes are reviewed by at least one other member of the engineering team, which is enforced through [branch protections](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches).

[benefits-repo]: https://github.com/cal-itp/benefits
[calitp]: https://calitp.org
[django]: https://docs.djangoproject.com/en/
[docker]: https://www.docker.com/products/docker-desktop
[interconnections]: deployment/infrastructure/#system-interconnections
[hosting]: deployment/
[littlepay]: https://littlepay.com/
[i18n]: https://docs.djangoproject.com/en/4.0/topics/i18n/
