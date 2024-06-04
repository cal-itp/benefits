# Application logic

!!! info "See also"

    More specific user flow diagrams: [Enrollment pathways](../enrollment-pathways/README.md)

This page describes how Cal-ITP Benefits defines user flows through the following high-level _phases_:

1. [Initial setup](#initial-setup)
1. [Identity proofing](#identity-proofing)
1. [Eligibility verification](#eligibility-verification)
1. [Enrollment](#enrollment)

```mermaid
flowchart LR
    start((Start))
    entry[Initial setup]
    identity[Identity proofing]
    eligibility[Eligibility verification]
    enrollment[Enrollment]
    complete((End))
    style complete stroke-width:2px

    start --> entry
    entry --> identity
    identity --> eligibility
    eligibility --> enrollment
    enrollment --> complete
```

The structure of the source code in [`benefits/`](https://github.com/cal-itp/benefits/tree/dev/benefits)
generally follows from these phases:

- [`benefits/core/`](https://github.com/cal-itp/benefits/tree/dev/benefits/core) implements shared logic and models, and
  defines the user's entrypoint into the app
- [`benefits/oauth/`](https://github.com/cal-itp/benefits/tree/dev/benefits/oauth) implements identity proofing
- [`benefits/eligibility/`](https://github.com/cal-itp/benefits/tree/dev/benefits/eligibility) implements eligibility
  verification
- [`benefits/enrollment/`](https://github.com/cal-itp/benefits/tree/dev/benefits/enrollment) implements enrollment

Each of these directories contains a standalone Django app registered in the [settings](../configuration/README.md#django-settings).

All of the common logic and [database models and migrations](./models-migrations.md) are defined in `benefits.core`, and this
app is imported by the other apps.

## Initial setup

In this phase, the user makes the initial selections that will configure the rest of their journey.

!!! example "Entrypoint"

    [`benefits/core/views.py`][core-views]

!!! example "Key supporting files"

    [`benefits/core/models.py`][core-models]

    [`benefits/core/session.py`][core-session]

```mermaid
flowchart LR
    session[(session)]
    start((Start))
    pick_agency["`Agency picker
    modal`"]
    agency(("`Agency
    selected`"))
    eligibility(("`Eligibility type
    selected`"))
    next>"`_Next phase_`"]
    style next stroke-width:2px

    start -- "1a. Lands on index" --> pick_agency
    start -- "1b. Lands on agency index" --> agency
    %% invisible links help with diagram layout
    start ~~~ session
    start ~~~ agency

    pick_agency -- 2. Chooses agency --> agency
    agency -- 3. Chooses enrollment pathway --> eligibility

    eligibility -- 4. continue --> next

    agency -. update -.-> session
    eligibility -. update -.-> session
```

Depending upon the choice of enrollment pathway, the _Next phase_ above may be:

- [Identity proofing](#identity-proofing), for all flows that require user PII (such as for verifying age).
- [Eligibility verification](#eligibility-verification), for Agency card flows that require a physical card from the transit
  agency.

## Identity proofing

In this phase, Cal-ITP Benefits takes the user through an [OpenID Connect (OIDC)](https://openid.net/developers/how-connect-works/)
flow as a Client (RP) of the CDT Identity Gateway (the Identity Provider or IDP), via Login.gov.

The CDT Identity Gateway transforms PII from Login.gov into anonymized boolean claims that are later used in
[eligibility verification](#eligibility-verification).

!!! example "Entrypoint"

    [`benefits/oauth/views.py`][oauth-views]

!!! example "Key supporting files"

    [`benefits/oauth/client.py`][oauth-client]

    [`benefits/oauth/redirects.py`][oauth-redirects]

```mermaid
flowchart LR
    session[(session)]

    start((Initial setup))
    style start stroke-dasharray: 5 5

    benefits[Benefits app]
    idg[["`CDT
    Identity Gateway`"]]
    logingov[[Login.gov]]
    claims((Claims received))

    next>"`_Eligibility
    verification_`"]
    style next stroke-width:2px

    start -- 1. Clicks login button --> benefits
    %% invisible links help with diagram layout
    start ~~~ session

    benefits -- 2. OIDC authorize_redirect --> idg
    idg <-. "3. PII exchange" .-> logingov
    idg -- 4. OIDC token authorization --> claims

    claims -- 5. continue --> next
    claims -. update .-> session
```

## Eligibility verification

In this phase, Cal-ITP Benefits verifies the user's claims using one of two methods:

- Claims validation, using claims previously stored in the user's session during [Identity proofing](#identity-proofing)
- Eligibility API verification, using non-PII claims provided by the user in an HTML form submission

!!! example "Entrypoint"

    [`benefits/eligibility/views.py`][eligibility-views]

!!! example "Key supporting files"

    [`benefits/eligibility/verify.py`][eligibility-verify]

```mermaid
flowchart LR
    session[(session)]

    start(("`Previous
    phase`"))
    style start stroke-dasharray: 5 5

    claims[Session claims check]
    form[HTTP form POST]
    server[[Eligibility Verification server]]
    eligible{Eligible?}

    next>"`_Enrollment_`"]
    style next stroke-width:2px

    stop{{Stop}}

    start -- Eligibility API verification --> form
    form -- Eligibility API call --> server
    server --> eligible

    start -- Claims validation --> claims
    session -. read .-> claims
    claims --> eligible

    eligible -- Yes --> next
    eligible -- No --> stop
    eligible -. update .-> session
```

## Enrollment

[core-models]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/models.py
[core-session]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/session.py
[core-views]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/views.py
[eligibility-verify]: https://github.com/cal-itp/benefits/blob/dev/benefits/eligibility/verify.py
[eligibility-views]: https://github.com/cal-itp/benefits/blob/dev/benefits/eligibility/views.py
[oauth-client]: https://github.com/cal-itp/benefits/blob/dev/benefits/oauth/client.py
[oauth-redirects]: https://github.com/cal-itp/benefits/blob/dev/benefits/oauth/redirects.py
[oauth-views]: https://github.com/cal-itp/benefits/blob/dev/benefits/oauth/views.py
