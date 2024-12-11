---
title: Introduction
---

# Enrollment pathways

This section describes in more detail some of the different enrollment pathways with current or planned support in the Benefits application.

## Current work

We do sprint planning and track day-to-day work on our [Project Board][board].

See our [Milestones][milestones] for current work tracked against specific features and different enrollment pathways.

## Product roadmap

Our product roadmap captures what we're currently building, what we've built, and what we plan to build in the future. We update it at the end of each quarter or when priorities change.

```mermaid
timeline
    title Cal-ITP Benefits Product Roadmap
%% Cal-ITP Benefits Epics (2024)
          section 2024

          Q1<br>Complete
          : Benefits admin tool (foundation)
          : Deploy SBMTD Reduced Fare Mobility ID enrollment pathway
          : Migrate to Littlepay Backoffice API

          Q2<br>Complete
          : Support for expiring benefits (low-income)
          : Improved UX for agency card enrollment
          : Improved UX for application error states

          Q3<br>Complete
          : Deploy low-income riders enrollment pathway
          : Benefits admin tool (agency users)
          : Benefits admin tool (in-person eligibility verification)

          Q4<br>Now
          : Deploy Medicare cardholder enrollment pathway
          : Support for multiple identity providers (Medicare.gov)

%% Cal-ITP Benefits Epics (2025)
          section 2025

          Q1<br>Next
        : Front-end enhancements and optimization
        : Benefits admin tool (user management)
        : Deploy in-person enrollments to all agencies
      %%: Deploy Connect Card enrollment pathway to SACOG agencies
        : Support for Discover and American Express cards

          Q2<br>Planned
        : Support for multiple fare processors (Enghouse)
        : Enhanced Veteran eligibility checks (disability status)
        : Single eligibility check across multiple benefit options
        : Benefits admin tool (agency configuration)

          H2<br>Projected
        : Eligibility check for individuals with disabilities (CA DMV)

%%{
    init: {
        'logLevel': 'debug',
        'theme': 'default' ,
        'themeVariables': {
            'cScale0': '#ffa500', 'cScaleLabel0': '#000000',
            'cScale1': '#ffff00', 'cScaleLabel1': '#000000',
            'cScale2': '#ffff00', 'cScaleLabel2': '#000000',
            'cScale3': '#008000', 'cScaleLabel3': '#ffffff',
            'cScale4': '#0000ff', 'cScaleLabel4': '#ffffff',
            'cScale5': '#4b0082', 'cScaleLabel5': '#ffffff',
            'cScale6': '#000000', 'cScaleLabel6': '#ffffff'
        }
    }
}%%
```
[board]: https://github.com/orgs/cal-itp/projects/8/views/1
[milestones]: https://github.com/cal-itp/benefits/milestones
