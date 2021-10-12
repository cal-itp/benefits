# Home

This website provides technical documentation for the [`benefits`][benefits-repo] application from the
[California Integrated Travel Project (Cal-ITP)][calitp].

Documentation for the `dev` (default) branch is available online at: <https://docs.calitp.org/benefits>.

## Overview

`benefits` is a [Django 3.x][django] web application enabling automated eligibility verification and enrollment for transit
benefits onto customers' existing contactless bank (credit/debit) cards.

The application implements an [Eligibility Verification API](https://docs.calitp.org/eligibility-verification/). Both the API and the application are
designed for privacy and security of user information:

* The API communicates with signed and encrypted JSON Web Tokens containing only the most necessary of user data
  for the purpose of eligibility verification
* The application requires no user accounts and stores no information about the user
* Interaction with the application is anonymous, with only minimal event tracking for usage and problem analysis

`benefits` is hosted in Amazon Web Services (AWS) [Elastic Container Service (ECS) on Fargate][ecs-fargate] and deployed with
GitHub Actions.

Running the application locally is possible with [Docker and Docker Compose][docker].

The user interface and content is available in both English and Spanish. Additional language support is possible via Django's
[i18n and l10n features][i18n].

[benefits-repo]: https://github.com/cal-itp/benefits
[calitp]: https://calitp.org
[django]: https://docs.djangoproject.com/en/
[docker]: https://www.docker.com/products/docker-desktop
[ecs-fargate]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html
[i18n]: https://docs.djangoproject.com/en/3.2/topics/i18n/
