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

## Eligibility verification

## Enrollment

[core-models]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/models.py
[core-session]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/session.py
[core-views]: https://github.com/cal-itp/benefits/blob/dev/benefits/core/views.py
