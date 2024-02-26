# Agency Cards

_Agency Cards_ is a generic term for reduced fare programs offered by Transit Providers, such as the
[Courtesy Card program from Monterey-Salinas Transit (MST)](https://mst.org/riders-guide/how-to-ride/courtesy-card/).

Agency cards are different from our other use cases in that eligibility verification happens on the agency side (offline) rather
than through the Benefits app, and the Benefits app then checks for a valid Agency Card via an [Eligibility API call](https://docs.calitp.org/eligibility-api/specification/).

## Demonstration

The video walkthough below demonstrates the flow for an agency card user to confirm transit benefit eligibility and enroll their bank card for reduced fares via LittlePay:

![Demonstration of the sign-up process for an agency card user confirming eligibility via the Eligibility Server and enrolling via Littlepay](https://github-production-user-asset-6210df.s3.amazonaws.com/6279581/305587680-67ee56d7-968e-4b53-838f-04fdf8cbb534.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAVCODYLSA53PQK4ZA%2F20240220%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20240220T214537Z&X-Amz-Expires=300&X-Amz-Signature=2d2ec95ef30cea975b05ed0e60774cabf502b980a9509244188c837cf83a1a4d&X-Amz-SignedHeaders=host&actor_id=3673236&key_id=0&repo_id=285501392){ width="350" }

## Architecture

In order to support an Agency Cards deployment, the Transit Provider produces a list of eligible users
(CSV format) that is loaded into an instance of [Eligibility Server](https://docs.calitp.org/eligibility-server/) running in the Transit Provider's cloud.

Cal-ITP makes the [`hashfields` tool](https://docs.calitp.org/hashfields) to facilitate masking user data before it leaves Transit Provider on-premises systems.

The complete system architecture looks like:

```mermaid
flowchart LR
    rider((User's browser))
    api[Eligibility Server]
    data[Hashed Agency Card data]
    cardsystem[Data source]

    rider --> Benefits

    subgraph CDT Azure
        Benefits
    end

    Benefits --> api

    subgraph Transit Provider cloud
        api --> data
    end

    subgraph Transit Provider on-prem
        cardsystem --> hashfields
    end

    hashfields --> data
```

Notes:

- [Eligibility Server source code](https://github.com/cal-itp/eligibility-server)
- [hashfields source code](https://github.com/cal-itp/hashfields)
- [More details about the Benefits architecture](../../deployment/infrastructure/#architecture)
- In MST, the `Data Source` is Velocity, the system MST uses to manage and print Courtesy Cards

## Process

```mermaid
sequenceDiagram
    actor Rider
    participant Benefits as Benefits app
    participant elig_server as Eligibility Server
    participant cc_data as Hashed data
    participant Data Source
    participant Littlepay

    Data Source-->>cc_data: exports nightly
    cc_data-->>elig_server: gets loaded on Server start

    Rider->>Benefits: visits site
    Benefits-->>elig_server: passes entered Agency Card details
    elig_server-->>Benefits: confirms eligibility

    Benefits-->>Littlepay: enrollment start
    Rider->>Littlepay: enters payment card details
    Littlepay-->>Benefits: enrollment complete
```
