# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/cal-itp/benefits/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                                           |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|----------------------------------------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| benefits/\_\_init\_\_.py                                                                       |        6 |        2 |        0 |        0 |     67% |       5-7 |
| benefits/admin.py                                                                              |       37 |        1 |        6 |        2 |     93% |57->73, 61 |
| benefits/apps.py                                                                               |        3 |        0 |        0 |        0 |    100% |           |
| benefits/core/\_\_init\_\_.py                                                                  |        0 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin/\_\_init\_\_.py                                                            |        6 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin/common.py                                                                  |        6 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin/enrollment.py                                                              |       60 |        2 |       26 |        3 |     92% |43->45, 45->48, 67-68 |
| benefits/core/admin/forms.py                                                                   |        6 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin/mixins.py                                                                  |       50 |        0 |        4 |        0 |    100% |           |
| benefits/core/admin/transit.py                                                                 |       15 |        0 |        4 |        0 |    100% |           |
| benefits/core/admin/users.py                                                                   |       58 |        0 |       14 |        1 |     99% |  95->exit |
| benefits/core/admin/views.py                                                                   |       21 |        0 |        0 |        0 |    100% |           |
| benefits/core/analytics.py                                                                     |       99 |       20 |       18 |        3 |     72% |136-138, 143, 149-171, 182 |
| benefits/core/apps.py                                                                          |        5 |        0 |        0 |        0 |    100% |           |
| benefits/core/context/\_\_init\_\_.py                                                          |        7 |        0 |        0 |        0 |    100% |           |
| benefits/core/context/agency.py                                                                |       18 |        0 |        0 |        0 |    100% |           |
| benefits/core/context/flow.py                                                                  |       16 |        1 |        0 |        0 |     94% |        25 |
| benefits/core/context\_processors.py                                                           |       48 |        5 |       14 |        4 |     85% |18, 35->38, 73-74, 83, 113 |
| benefits/core/forms.py                                                                         |       24 |        0 |        4 |        0 |    100% |           |
| benefits/core/middleware.py                                                                    |       84 |        9 |       20 |        4 |     88% |37-38, 49-50, 57-58, 77->82, 104-105, 132 |
| benefits/core/mixins.py                                                                        |       46 |        2 |       10 |        0 |     96% |     72-73 |
| benefits/core/models/\_\_init\_\_.py                                                           |        4 |        0 |        0 |        0 |    100% |           |
| benefits/core/models/common.py                                                                 |       51 |        2 |       14 |        0 |     97% |     91-92 |
| benefits/core/models/enrollment.py                                                             |      150 |        3 |       28 |        3 |     97% |140, 157, 241->252, 276 |
| benefits/core/models/transit.py                                                                |      146 |        0 |       34 |        0 |    100% |           |
| benefits/core/recaptcha.py                                                                     |       13 |        5 |        4 |        1 |     53% |     26-32 |
| benefits/core/session.py                                                                       |      131 |        3 |       32 |        0 |     98% |     53-55 |
| benefits/core/urls.py                                                                          |       25 |        0 |        2 |        0 |    100% |           |
| benefits/core/views.py                                                                         |       81 |        6 |        4 |        0 |     91% | 90, 93-99 |
| benefits/core/widgets.py                                                                       |       25 |        5 |        6 |        2 |     71% |17, 18->exit, 38-43 |
| benefits/eligibility/\_\_init\_\_.py                                                           |        0 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/analytics.py                                                              |       27 |        3 |        2 |        1 |     86% |21, 39->exit, 45, 55 |
| benefits/eligibility/apps.py                                                                   |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/context/\_\_init\_\_.py                                                   |        2 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/context/flow.py                                                           |       29 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/forms.py                                                                  |       60 |        0 |       12 |        6 |     92% |111->113, 113->115, 115->117, 117->121, 128->130, 130->134 |
| benefits/eligibility/urls.py                                                                   |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/verify.py                                                                 |       12 |        0 |        4 |        0 |    100% |           |
| benefits/eligibility/views.py                                                                  |      101 |        3 |       18 |        1 |     95% |22->25, 128-130 |
| benefits/enrollment/\_\_init\_\_.py                                                            |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/analytics.py                                                               |       30 |        3 |       12 |        2 |     88% |24->exit, 29, 56, 75 |
| benefits/enrollment/apps.py                                                                    |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/context/\_\_init\_\_.py                                                    |        2 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/context/flow.py                                                            |       18 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/enrollment.py                                                              |       47 |        1 |       10 |        2 |     95% |71, 113->exit |
| benefits/enrollment/forms.py                                                                   |       14 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/urls.py                                                                    |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/views.py                                                                   |       85 |        1 |        8 |        1 |     98% |       179 |
| benefits/enrollment\_littlepay/\_\_init\_\_.py                                                 |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/admin.py                                                        |        9 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/apps.py                                                         |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/enrollment.py                                                   |       80 |        0 |       26 |        1 |     99% |  159->158 |
| benefits/enrollment\_littlepay/migrations/0001\_initial.py                                     |        7 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/migrations/0002\_littlepaygroup.py                              |       18 |        8 |        4 |        1 |     50% |     13-21 |
| benefits/enrollment\_littlepay/migrations/0003\_rename\_littlepayconfig\_oldlittlepayconfig.py |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/migrations/0004\_littlepayconfig.py                             |       15 |        4 |        4 |        1 |     63% |     14-25 |
| benefits/enrollment\_littlepay/migrations/0005\_delete\_oldlittlepayconfig.py                  |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/migrations/\_\_init\_\_.py                                      |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/models.py                                                       |       29 |        0 |        8 |        0 |    100% |           |
| benefits/enrollment\_littlepay/session.py                                                      |       35 |        0 |        8 |        0 |    100% |           |
| benefits/enrollment\_littlepay/urls.py                                                         |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/views.py                                                        |       80 |        5 |       12 |        2 |     90% |37->50, 102-106 |
| benefits/enrollment\_switchio/\_\_init\_\_.py                                                  |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/admin.py                                                         |        9 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/api.py                                                           |      119 |        1 |       10 |        1 |     98% |       208 |
| benefits/enrollment\_switchio/apps.py                                                          |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/enrollment.py                                                    |      115 |        0 |       36 |        3 |     98% |97->100, 145->142, 239->238 |
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
| benefits/in\_person/context/eligibility.py                                                     |        7 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/forms.py                                                                   |       42 |        9 |        6 |        0 |     73% |     59-70 |
| benefits/in\_person/mixins.py                                                                  |        7 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/urls.py                                                                    |        6 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/views.py                                                                   |      115 |        1 |        8 |        1 |     98% |       196 |
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
| benefits/settings.py                                                                           |      129 |        8 |       24 |        9 |     89% |109, 130->135, 146->149, 166, 344, 354, 360, 369, 393-394 |
| benefits/urls.py                                                                               |       30 |        7 |        4 |        2 |     74% |37->48, 52-66 |
| benefits/wsgi.py                                                                               |        4 |        4 |        0 |        0 |      0% |     10-17 |
|                                                                                      **TOTAL** | **3158** |  **155** |  **534** |   **61** | **93%** |           |


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