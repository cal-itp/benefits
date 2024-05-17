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
          : Benefits admin tool (Foundation)
          : SBMTD - Launch Reduced Fare Mobility ID enrollment pathway
          : Migrate to Littlepay Backoffice API

          Q2<br>Now
          : Deploy low-income riders enrollment pathway
          : Support for expiring benefits (low-income)
          : Improved UX for agency card enrollment
          : Improved UX for application error states
          %% : Release enhancements to Veterans pathway

          Q3<br>Next
          : Benefits admin tool (Agency configuration)
          : Benefits admin tool (Agency users)
          : Release Medicare cardholder enrollment pathway

          Q4<br>Planned
          : Benefits admin tool (In-person eligibility verification)
          : Release riders with disabilities enrollment pathway

%% Cal-ITP Benefits Epics (2025)
          section 2025

          Q1
          : Support benefits reciprocity between CA transit agencies
          : Implement evolved organizing principles for app UX

          Q2
          : Support for multiple payment processors
          : Integration with all MSA payment processors

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
