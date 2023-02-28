---
name: Incident response
about: Use to track the steps that should happen during an incident, such as a data breach or unexpected downtime, even if it's just a suspicion.
---

_**Do not put sensitive information in this issue or Slack.** Use a file on Google Drive with access restricted._

**Severity:** _High/Medium/Low_

## Initiate

1. [x] Create an issue from this template.
1. [ ] Declare an incident in the relevant Slack channel, such as [#benefits-general][benefits-general].
   - Include brief details about the concern.
1. [ ] Start a video call.
1. [ ] Share a link to the video call in Slack, asking relevant parties to join.
1. [ ] Delegate subsequent tasks.

## Assess

- [ ] Determine the impact.
- [ ] Assign the severity above:
  - **High:** Possible/confirmed breach of sensitive information, such as production system credentials or personally-identifiable information (PII)
  - **Medium:** Full Benefits downtime for more than 30 minutes
  - **Low:** Partial service degredation

### Medium/High incidents

- [ ] Notify [#benefits-general][benefits-general].
- [ ] If the incident is lasting more than 60 minutes or their customers' data has been breached, notify the impacted transit agencies.
- [ ] If it's believed to be an ongoing attack (such as DDoS), notify DevSecOps.

## Remediate

- [ ] Take notes in the Slack thread.
- [ ] Check the [troubleshooting documentation](https://docs.calitp.org/benefits/deployment/troubleshooting/) for relevant information.
- [ ] Post in the Slack thread when the incident has been resolved.
- [ ] Retain any relevant materials.

### Medium/High incidents

- [ ] Provide updates to [#benefits-general][benefits-general] every 30 minutes.
- [ ] [Release hotfixes](https://docs.calitp.org/benefits/deployment/release/) as necessary.
- [ ] Notify [#benefits-general][benefits-general] when the incident has been resolved.

## Follow-up

- [ ] For Medium/High incidents, write an incident report. [Past examples.](https://drive.google.com/drive/search?q=parent:1f_UhA3958lrRQ7IVf0mGSpt7A9rSoUQm%20title:incident)
  1. [ ] Write a draft.
     - Link to relevant Slack messages, etc.
  1. [ ] Get thumbs-up from those involved in the incident.
  1. [ ] Share with relevant stakeholders.
- [ ] Create issues for follow-up tasks, such as:
  - Adding monitoring
  - Updating documentation
  - Having the system fail more gracefully
  - Scheduling a retrospective/post-mortem

[benefits-general]: https://cal-itp.slack.com/archives/c013w8ruamu
