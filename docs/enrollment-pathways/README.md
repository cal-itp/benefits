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

          Q4<br>Complete
          : Deploy Medicare cardholder enrollment pathway
          : Support for multiple identity providers (Medicare.gov)

%% Cal-ITP Benefits Epics (2025)
          section 2025

          Q1<br>Complete
        : Front-end enhancements and optimization
        : Deploy in-person enrollments
        : Utilize CDT Identity Gateway connection library

          Q2<br>Complete
        : Support for Discover and American Express cards

          Q3<br>Now
        : Support for multiple transit processors (Enghouse)
        : UI enhancements to help the application scale
        : Benefits admin tool (user management)

          Q4<br>Projected
        : Enhanced Veteran eligibility checks (disability status)
        : Support for additional identity provider (Socure)
        : Single eligibility check across multiple benefit options
        : Eligibility check for individuals with disabilities (CA DMV)

%%{
  init: {
    'logLevel': 'debug',
    'theme': 'default' ,
    'themeVariables': {
      'cScale0': 'orange',
      'cScaleLabel0': 'black',
      'cScale1': 'yellow',
      'cScaleLabel1': 'black'
    }
  }
}%%
```

[board]: https://github.com/orgs/compilerla/projects/6/views/8
[milestones]: https://github.com/cal-itp/benefits/milestones
