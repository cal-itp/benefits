# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/cal-itp/benefits/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                                           |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|----------------------------------------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| benefits/\_\_init\_\_.py                                                                       |        6 |        2 |        0 |        0 |     67% |       5-7 |
| benefits/admin.py                                                                              |       40 |        4 |        8 |        2 |     83% |18-20, 61->77, 65 |
| benefits/apps.py                                                                               |        3 |        0 |        0 |        0 |    100% |           |
| benefits/core/\_\_init\_\_.py                                                                  |        0 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin/\_\_init\_\_.py                                                            |        5 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin/common.py                                                                  |       13 |        0 |        4 |        0 |    100% |           |
| benefits/core/admin/enrollment.py                                                              |       97 |        7 |       48 |        6 |     90% |24, 36, 40, 46, 107-108, 164 |
| benefits/core/admin/transit.py                                                                 |       22 |        1 |        8 |        1 |     93% |        45 |
| benefits/core/admin/users.py                                                                   |       40 |        0 |        8 |        1 |     98% |  46->exit |
| benefits/core/analytics.py                                                                     |       99 |       20 |       18 |        3 |     72% |136-138, 143, 149-171, 182 |
| benefits/core/apps.py                                                                          |        5 |        0 |        0 |        0 |    100% |           |
| benefits/core/context/\_\_init\_\_.py                                                          |        7 |        0 |        0 |        0 |    100% |           |
| benefits/core/context/agency.py                                                                |       17 |        0 |        0 |        0 |    100% |           |
| benefits/core/context/flow.py                                                                  |       19 |        0 |        0 |        0 |    100% |           |
| benefits/core/context\_processors.py                                                           |       50 |        2 |       14 |        2 |     94% |37->45, 90, 120 |
| benefits/core/middleware.py                                                                    |       84 |        5 |       20 |        3 |     92% |37-38, 57-58, 77->82, 132 |
| benefits/core/mixins.py                                                                        |       31 |        0 |        8 |        0 |    100% |           |
| benefits/core/models/\_\_init\_\_.py                                                           |        4 |        0 |        0 |        0 |    100% |           |
| benefits/core/models/common.py                                                                 |       51 |        2 |       14 |        0 |     97% |     91-92 |
| benefits/core/models/enrollment.py                                                             |      157 |        3 |       32 |        3 |     97% |142, 159, 252->263, 287 |
| benefits/core/models/transit.py                                                                |      136 |        0 |       30 |        0 |    100% |           |
| benefits/core/recaptcha.py                                                                     |       13 |        5 |        4 |        1 |     53% |     26-32 |
| benefits/core/session.py                                                                       |      131 |        3 |       32 |        0 |     98% |     53-55 |
| benefits/core/urls.py                                                                          |       25 |        0 |        2 |        0 |    100% |           |
| benefits/core/views.py                                                                         |       68 |        0 |        2 |        0 |    100% |           |
| benefits/core/widgets.py                                                                       |       25 |        5 |        6 |        2 |     71% |17, 18->exit, 38-43 |
| benefits/eligibility/\_\_init\_\_.py                                                           |        0 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/analytics.py                                                              |       27 |        3 |        2 |        1 |     86% |21, 39->exit, 45, 55 |
| benefits/eligibility/apps.py                                                                   |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/context/\_\_init\_\_.py                                                   |        2 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/context/flow.py                                                           |       37 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/forms.py                                                                  |       65 |        2 |       16 |        8 |     88% |41, 114->116, 116->118, 118->120, 120->124, 131->133, 133->137, 141 |
| benefits/eligibility/urls.py                                                                   |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/verify.py                                                                 |       12 |        0 |        4 |        0 |    100% |           |
| benefits/eligibility/views.py                                                                  |      101 |        3 |       18 |        1 |     95% |22->25, 116-118 |
| benefits/enrollment/\_\_init\_\_.py                                                            |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/analytics.py                                                               |       21 |        4 |        6 |        2 |     78% |21->23, 24, 38, 43, 48 |
| benefits/enrollment/apps.py                                                                    |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/context/\_\_init\_\_.py                                                    |        2 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/context/flow.py                                                            |       34 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/enrollment.py                                                              |       35 |        1 |       10 |        2 |     93% |46, 70->exit |
| benefits/enrollment/forms.py                                                                   |       14 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/urls.py                                                                    |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/views.py                                                                   |       50 |        1 |        6 |        1 |     96% |        51 |
| benefits/enrollment\_littlepay/\_\_init\_\_.py                                                 |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/admin.py                                                        |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/apps.py                                                         |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/enrollment.py                                                   |       98 |        0 |       26 |        1 |     99% |  166->165 |
| benefits/enrollment\_littlepay/migrations/0001\_initial.py                                     |        7 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/migrations/0002\_littlepaygroup.py                              |       18 |        8 |        4 |        1 |     50% |     13-21 |
| benefits/enrollment\_littlepay/migrations/0003\_rename\_littlepayconfig\_oldlittlepayconfig.py |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/migrations/0004\_littlepayconfig.py                             |       15 |        4 |        4 |        1 |     63% |     14-25 |
| benefits/enrollment\_littlepay/migrations/0005\_delete\_oldlittlepayconfig.py                  |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/migrations/\_\_init\_\_.py                                      |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/models.py                                                       |       29 |        0 |        8 |        0 |    100% |           |
| benefits/enrollment\_littlepay/session.py                                                      |       35 |        0 |        8 |        0 |    100% |           |
| benefits/enrollment\_littlepay/urls.py                                                         |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/views.py                                                        |       79 |        5 |       12 |        2 |     90% |36->49, 101-105 |
| benefits/enrollment\_switchio/\_\_init\_\_.py                                                  |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/admin.py                                                         |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/api.py                                                           |      119 |        0 |        2 |        0 |    100% |           |
| benefits/enrollment\_switchio/apps.py                                                          |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/enrollment.py                                                    |      109 |        0 |       28 |        4 |     97% |96->99, 144->141, 167->202, 209->208 |
| benefits/enrollment\_switchio/migrations/0001\_initial.py                                      |        8 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/migrations/0002\_switchioconfig\_enrollment\_api.py              |        6 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/migrations/0003\_switchiogroup.py                                |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/migrations/0004\_rename\_switchioconfig\_oldswitchioconfig.py    |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/migrations/0005\_switchioconfig\_delete\_oldswitchioconfig.py    |        7 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/migrations/\_\_init\_\_.py                                       |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/models.py                                                        |       49 |        0 |       12 |        0 |    100% |           |
| benefits/enrollment\_switchio/session.py                                                       |       28 |        0 |        6 |        0 |    100% |           |
| benefits/enrollment\_switchio/urls.py                                                          |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/views.py                                                         |      107 |        0 |       26 |        2 |     98% |91->102, 99->102 |
| benefits/in\_person/\_\_init\_\_.py                                                            |        0 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/apps.py                                                                    |        4 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/context/\_\_init\_\_.py                                                    |        2 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/context/eligibility.py                                                     |        8 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/forms.py                                                                   |       42 |        9 |        6 |        0 |     73% |     59-70 |
| benefits/in\_person/urls.py                                                                    |        6 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/views.py                                                                   |      122 |        1 |        8 |        1 |     98% |       226 |
| benefits/locale/\_\_init\_\_.py                                                                |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/en/\_\_init\_\_.py                                                             |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/en/formats.py                                                                  |        1 |        0 |        0 |        0 |    100% |           |
| benefits/locale/es/\_\_init\_\_.py                                                             |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/es/formats.py                                                                  |        1 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/\_\_init\_\_.py                                                                 |        0 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/analytics.py                                                                    |       41 |       11 |        4 |        0 |     76% |30, 37, 53, 60-61, 66, 71, 76, 81, 86, 91 |
| benefits/oauth/apps.py                                                                         |        5 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/hooks.py                                                                        |       56 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/middleware.py                                                                   |       23 |        0 |        6 |        0 |    100% |           |
| benefits/oauth/urls.py                                                                         |       12 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/views.py                                                                        |        8 |        0 |        0 |        0 |    100% |           |
| benefits/routes.py                                                                             |      116 |        0 |        0 |        0 |    100% |           |
| benefits/secrets.py                                                                            |       48 |        8 |       10 |        1 |     81% |     90-99 |
| benefits/sentry.py                                                                             |       57 |       12 |       10 |        1 |     81% |19, 24-25, 30, 34-35, 63-64, 87-108 |
| benefits/settings.py                                                                           |      132 |        7 |       24 |        9 |     90% |106, 127->132, 143->146, 163, 319, 331, 333, 348, 360 |
| benefits/urls.py                                                                               |       27 |        7 |        4 |        2 |     71% |35->46, 50-64 |
| benefits/wsgi.py                                                                               |        4 |        4 |        0 |        0 |      0% |     10-17 |
|                                                                                      **TOTAL** | **3040** |  **149** |  **528** |   **64** | **93%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/cal-itp/benefits/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/cal-itp/benefits/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/cal-itp/benefits/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/cal-itp/benefits/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fcal-itp%2Fbenefits%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/cal-itp/benefits/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.