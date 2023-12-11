# Analytics

## Information not collected

- IP Address
- Designated Market Area (DMA)

See the [Amplitude analytics code on GitHub](https://github.com/cal-itp/benefits/blob/dev/benefits/core/templates/core/includes/analytics.html#L30).

## User information collected

### Default Amplitude user properties collected

- Platform
- Device type
- Device family
- Country
- City
- Region
- Start version
- Version
- Carrier
- OS: Operating system name and version
- Language
- Library

Read more about each property on the [Amplitude documentation](https://help.amplitude.com/hc/en-us/articles/215562387-Appendix-Amplitude-User-Property-Definitions).

### Custom user properties collected

| Custom user property   | Description                        | Example value                                                                                                     |
| ---------------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `eligibility_types`    | Eligibility type chosen by user    | `[veteran]`                                                                                                       |
| `eligibility_verifier` | Eligibility verifier used by user  | `VA.gov - Veteran (MST)`                                                                                          |
| `referrer`             | URL that the event came from       | https://benefits.calitp.org/eligibility/start                                                                     |
| `referring_domain`     | Domain that the event came from    | `benefits.calitp.org`                                                                                             |
| `transit_agency`       | Agency chosen by the user          | `Monterey-Salinas Transit`                                                                                        |
| `user_agent`           | User's browser agent               | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36` |

## Event information collected

Information is collected on key user actions on the app, called events. Each event is categorized within one of four categories: core, authentication, eligibility or enrollment.

- https://data.amplitude.com/public-doc/hdhfmlby2e

### Core events

Read more on each of these events on the [Amplitude event documentation for Benefits](https://data.amplitude.com/public-doc/hdhfmlby2e?categories=id%3D1702329985270%26group%3Dcategories%26type%3DString%26operator%3Dis%26values%255B0%255D%3Dcore%26dateValue%255Btype%255D%3DSINCE)

### Authentication events

Read more on each of these events on the [Amplitude event documentation for Benefits](https://data.amplitude.com/public-doc/hdhfmlby2e?categories=id%3D1702329910563%26group%3Dcategories%26type%3DString%26operator%3Dis%26values%255B0%255D%3Doauth%26dateValue%255Btype%255D%3DSINCE)

### Eligibility events

Read more on each of these events on the [Amplitude event documentation for Benefits](https://data.amplitude.com/public-doc/hdhfmlby2e?categories=id%3D1702329975970%26group%3Dcategories%26type%3DString%26operator%3Dis%26values%255B0%255D%3Deligibility%26dateValue%255Btype%255D%3DSINCE)

### Enrollment events

Read more on each of these events on the [Amplitude event documentation for Benefits](https://data.amplitude.com/public-doc/hdhfmlby2e?categories=id%3D1702329910563%26group%3Dcategories%26type%3DString%26operator%3Dis%26values%255B0%255D%3Denrollment%26dateValue%255Btype%255D%3DSINCE)

## Key metrics

- Number of users who successfully completed authentication: Users who `started sign in`, `finished sign in`
- Number of users who successfully completed eligibility and received a status of True: Users who `selected eligibility verifier`, `started eligibility`, `returned eligibility` with a status of `True`
- Numbers of users who successfully completed enrollment: Users who `started payment connection`, `closed payment connection` and `returned enrollment` with a status of `Success`
