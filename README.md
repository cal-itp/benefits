# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/cal-itp/benefits/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                       |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|----------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| benefits/\_\_init\_\_.py                                   |        6 |        2 |        0 |        0 |     67% |       5-7 |
| benefits/admin.py                                          |       38 |        1 |        6 |        2 |     93% |57->76, 61 |
| benefits/apps.py                                           |        3 |        0 |        0 |        0 |    100% |           |
| benefits/core/\_\_init\_\_.py                              |        0 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin/\_\_init\_\_.py                        |        6 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin/common.py                              |        6 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin/enrollment.py                          |       44 |        0 |       12 |        2 |     96% |48->50, 50->54 |
| benefits/core/admin/forms.py                               |       18 |        0 |        2 |        0 |    100% |           |
| benefits/core/admin/mixins.py                              |       50 |        0 |        4 |        0 |    100% |           |
| benefits/core/admin/transit.py                             |       26 |        0 |        8 |        0 |    100% |           |
| benefits/core/admin/users.py                               |       50 |        0 |       10 |        0 |    100% |           |
| benefits/core/admin/views.py                               |       26 |        0 |        0 |        0 |    100% |           |
| benefits/core/analytics.py                                 |       99 |       20 |       18 |        3 |     72% |138-140, 145, 151-173, 184 |
| benefits/core/apps.py                                      |       16 |        0 |        2 |        1 |     94% |  31->exit |
| benefits/core/context\_processors.py                       |       48 |        7 |       10 |        3 |     79% |29->32, 62-70, 77, 112 |
| benefits/core/forms.py                                     |       24 |        0 |        4 |        0 |    100% |           |
| benefits/core/management/commands/\_\_init\_\_.py          |        0 |        0 |        0 |        0 |    100% |           |
| benefits/core/management/commands/ensure\_db.py            |      183 |        4 |       42 |        4 |     96% |73, 87-89, 99, 103->exit, 230->232, 306->310 |
| benefits/core/middleware.py                                |       84 |       12 |       20 |        3 |     84% |36-37, 44-49, 56-57, 76->81, 103-104, 131 |
| benefits/core/mixins.py                                    |       48 |        2 |       10 |        0 |     97% |     74-75 |
| benefits/core/models/\_\_init\_\_.py                       |        4 |        0 |        0 |        0 |    100% |           |
| benefits/core/models/common.py                             |       52 |        2 |       14 |        0 |     97% |     91-92 |
| benefits/core/models/enrollment.py                         |      133 |        3 |       18 |        3 |     96% |184, 192, 215 |
| benefits/core/models/transit.py                            |      155 |        0 |       44 |        1 |     99% |  261->272 |
| benefits/core/recaptcha.py                                 |       13 |        5 |        4 |        1 |     53% |     24-30 |
| benefits/core/session.py                                   |      151 |        3 |       40 |        0 |     98% |     56-58 |
| benefits/core/urls.py                                      |       27 |        2 |        2 |        1 |     90% |     38-39 |
| benefits/core/views.py                                     |       93 |        8 |        8 |        1 |     89% |105, 115, 129-131, 138-229 |
| benefits/core/widgets.py                                   |       25 |        5 |        6 |        1 |     74% | 18, 39-44 |
| benefits/eligibility/\_\_init\_\_.py                       |        0 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/analytics.py                          |       27 |        4 |        2 |        1 |     83% |21, 39->exit, 45, 55, 60 |
| benefits/eligibility/apps.py                               |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/forms.py                              |       85 |        0 |       14 |        2 |     98% |106->108, 108->112 |
| benefits/eligibility/urls.py                               |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/verify.py                             |       12 |        0 |        4 |        0 |    100% |           |
| benefits/eligibility/views.py                              |      123 |        3 |       16 |        0 |     96% |     77-79 |
| benefits/enrollment/\_\_init\_\_.py                        |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/analytics.py                           |       30 |        0 |       12 |        1 |     98% |  25->exit |
| benefits/enrollment/apps.py                                |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/enrollment.py                          |       50 |        0 |       12 |        1 |     98% | 124->exit |
| benefits/enrollment/forms.py                               |       14 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/urls.py                                |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/views.py                               |      104 |        0 |       10 |        0 |    100% |           |
| benefits/enrollment\_littlepay/\_\_init\_\_.py             |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/admin.py                    |        9 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/apps.py                     |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/enrollment.py               |       80 |        0 |       26 |        1 |     99% |  158->157 |
| benefits/enrollment\_littlepay/migrations/0001\_initial.py |        8 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/migrations/\_\_init\_\_.py  |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/models.py                   |       37 |        1 |       10 |        1 |     96% |        50 |
| benefits/enrollment\_littlepay/session.py                  |       35 |        0 |        8 |        0 |    100% |           |
| benefits/enrollment\_littlepay/urls.py                     |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_littlepay/views.py                    |       78 |        5 |       12 |        2 |     90% |37->50, 103-107 |
| benefits/enrollment\_switchio/\_\_init\_\_.py              |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/admin.py                     |        9 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/api.py                       |      119 |        1 |       10 |        1 |     98% |       209 |
| benefits/enrollment\_switchio/apps.py                      |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/enrollment.py                |      115 |        0 |       36 |        3 |     98% |98->101, 146->143, 242->241 |
| benefits/enrollment\_switchio/migrations/0001\_initial.py  |        8 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/migrations/\_\_init\_\_.py   |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/models.py                    |       59 |        0 |       16 |        0 |    100% |           |
| benefits/enrollment\_switchio/session.py                   |       28 |        0 |        6 |        0 |    100% |           |
| benefits/enrollment\_switchio/urls.py                      |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment\_switchio/views.py                     |      108 |        0 |       26 |        2 |     99% |91->102, 99->102 |
| benefits/in\_person/\_\_init\_\_.py                        |        0 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/apps.py                                |        4 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/forms.py                               |       43 |        9 |        6 |        0 |     73% |     81-92 |
| benefits/in\_person/mixins.py                              |        7 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/urls.py                                |        6 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/views.py                               |      116 |        1 |        8 |        1 |     98% |       209 |
| benefits/locale/\_\_init\_\_.py                            |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/en/\_\_init\_\_.py                         |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/en/formats.py                              |        1 |        0 |        0 |        0 |    100% |           |
| benefits/locale/es/\_\_init\_\_.py                         |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/es/formats.py                              |        1 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/\_\_init\_\_.py                             |        0 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/analytics.py                                |       41 |       11 |        4 |        0 |     76% |30, 37, 53, 60-61, 66, 71, 76, 81, 86, 91 |
| benefits/oauth/apps.py                                     |        5 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/hooks.py                                    |       56 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/middleware.py                               |       23 |        0 |        6 |        0 |    100% |           |
| benefits/oauth/urls.py                                     |       12 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/views.py                                    |        8 |        0 |        0 |        0 |    100% |           |
| benefits/routes.py                                         |      119 |        0 |        0 |        0 |    100% |           |
| benefits/secrets.py                                        |       48 |        8 |       10 |        1 |     81% |     90-99 |
| benefits/sentry.py                                         |       55 |       12 |       10 |        1 |     80% |16, 21-22, 27, 31-32, 60-61, 93-118 |
| benefits/settings.py                                       |      132 |        9 |       26 |       10 |     88% |108, 129->134, 145->148, 165, 189, 363, 373, 379, 388, 412-413 |
| benefits/urls.py                                           |       46 |        9 |        6 |        2 |     75% |43->82, 57, 60, 63, 66, 69-71, 82->94, 88-90 |
| benefits/views.py                                          |       33 |        0 |        0 |        0 |    100% |           |
| benefits/wsgi.py                                           |        4 |        4 |        0 |        0 |      0% |     10-16 |
| **TOTAL**                                                  | **3364** |  **153** |  **580** |   **56** | **94%** |           |


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