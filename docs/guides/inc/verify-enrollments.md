## Verify real user enrollments are starting to happen

### Amplitude

![Amplitude chart config with settings described in detail below](img/amplitude-verification-query.png){ align=right }

We consider a transit provider officially onboarded to Cal-ITP Benefits when the transit provider appears in our metrics. Specifically, the transit provider is onboarded when we see one or more complete enrollments for that transit provider in [Amplitude](https://amplitude.com/).

Use this query to confirm:

- **Segment:** All Users
- **Measured as:** Event Totals
- **Events:** Completed enrollment
  - User property `enrollment_method`: `digital`, `in_person`
  - Grouped by: `transit_agency`

You can also go directly to the existing [Enrollments by transit provider](https://app.amplitude.com/analytics/compiler/chart/mccedr54/edit/o9xupwel) chart.

### Metabase { .clear }

Amplitude currently stores only a year of historical data, so we archive all Cal-ITP data in [Metabase](https://www.metabase.com/). Thus, we also need to ensure metrics for the new transit provider are successfully piped from Amplitude to Metabase.

Use this query to confirm:

![Metabase chart config with settings described in detail below](img/metabase-verification-query.png)

- **Data:** Fct Benefits Events
- **Filter:**
  - Event Type is returned enrollment
  - Event Properties Status is success
  - Event Time is [some date range that includes the dates you're expecting to see data for the new transit provider]
- **Summarize:** Count by Event Properties Transit Agency

You can also go directly to the existing [Cal-ITP Benefits enrollments by transit provider 2025](https://dashboards.calitp.org/question/3762-cal-itp-benefits-enrollments-by-transit-provider-2025) chart.
