# Home

This website provides technical documentation for the [`benefits`](https://github.com/cal-itp/benefits) application
from the [California Integrated Travel Project (Cal-ITP)](https://www.calitp.org).

Documentation for the `main` branch is available online at: <https://docs.calitp.org/benefits>.

## Overview

`benefits` is a [Django 3.x](https://docs.djangoproject.com/en/) web application enabling automated eligibility verification
and enrollment for transit benefits onto customers' existing contactless bank (credit/debit) cards.

The application implements an Eligibility Verification API designed for privacy and security of user information:

* The application requires no login credentials, and stores no information about the user.
* Interaction with the application is anonymous, with only minimal event tracking for usage and problem analysis.

`benefits` is hosted in Amazon Web Services (AWS) [Fargate](https://aws.amazon.com/fargate) and deployed with GitHub Actions.
Running the application locally is done via Docker and Docker Compose.

The user interface and content is available in both English and Spanish. Further language support is a quick drop-in with
Django's [i18n and l10n support](https://docs.djangoproject.com/en/3.2/topics/i18n/).
