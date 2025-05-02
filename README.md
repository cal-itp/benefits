# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/cal-itp/benefits/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                         |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| benefits/\_\_init\_\_.py                     |        6 |        2 |        0 |        0 |     67% |       5-7 |
| benefits/admin.py                            |       38 |        3 |        6 |        1 |     86% |18-20, 61->73 |
| benefits/apps.py                             |        3 |        0 |        0 |        0 |    100% |           |
| benefits/core/\_\_init\_\_.py                |        0 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin/\_\_init\_\_.py          |        5 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin/common.py                |       13 |        0 |        4 |        0 |    100% |           |
| benefits/core/admin/enrollment.py            |       98 |        7 |       48 |        6 |     90% |24, 36, 40, 46, 108-109, 166 |
| benefits/core/admin/transit.py               |       43 |        1 |       14 |        1 |     96% |        67 |
| benefits/core/admin/users.py                 |       40 |        0 |        8 |        1 |     98% |  46->exit |
| benefits/core/analytics.py                   |       99 |       20 |       18 |        3 |     72% |136-138, 143, 149-171, 182 |
| benefits/core/apps.py                        |        5 |        0 |        0 |        0 |    100% |           |
| benefits/core/context/\_\_init\_\_.py        |        7 |        0 |        0 |        0 |    100% |           |
| benefits/core/context/agency.py              |       15 |        0 |        0 |        0 |    100% |           |
| benefits/core/context/flow.py                |       19 |        0 |        0 |        0 |    100% |           |
| benefits/core/context\_processors.py         |       48 |        2 |       14 |        2 |     94% |35->43, 88, 113 |
| benefits/core/middleware.py                  |       84 |        3 |       20 |        2 |     95% |57-58, 77->82, 132 |
| benefits/core/mixins.py                      |       19 |        0 |        4 |        0 |    100% |           |
| benefits/core/models/\_\_init\_\_.py         |        4 |        0 |        0 |        0 |    100% |           |
| benefits/core/models/common.py               |       48 |        2 |       14 |        0 |     97% |     86-87 |
| benefits/core/models/enrollment.py           |      151 |        1 |       26 |        2 |     98% |153, 249->260 |
| benefits/core/models/transit.py              |      209 |       12 |       44 |        4 |     92% |70-74, 145-146, 150, 348, 360-363, 383->387 |
| benefits/core/recaptcha.py                   |       13 |        5 |        4 |        1 |     53% |     26-32 |
| benefits/core/session.py                     |      140 |        1 |       36 |        0 |     99% |        53 |
| benefits/core/urls.py                        |       25 |        0 |        2 |        0 |    100% |           |
| benefits/core/views.py                       |       65 |        0 |        2 |        0 |    100% |           |
| benefits/core/widgets.py                     |       25 |        1 |        6 |        3 |     87% |17, 18->exit, 40->43 |
| benefits/eligibility/\_\_init\_\_.py         |        0 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/analytics.py            |       27 |        4 |        2 |        1 |     83% |21, 39->exit, 45, 55, 60 |
| benefits/eligibility/apps.py                 |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/context/\_\_init\_\_.py |        3 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/context/agency.py       |        9 |        0 |        2 |        1 |     91% |      6->9 |
| benefits/eligibility/context/flow.py         |       37 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/forms.py                |       65 |        2 |       16 |        2 |     95% |   41, 141 |
| benefits/eligibility/urls.py                 |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/verify.py               |       12 |        0 |        4 |        0 |    100% |           |
| benefits/eligibility/views.py                |       82 |        1 |       20 |        2 |     97% |48, 93->exit |
| benefits/enrollment/\_\_init\_\_.py          |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/analytics.py             |       21 |        4 |        6 |        3 |     74% |21->23, 24, 32->exit, 43, 48, 61 |
| benefits/enrollment/apps.py                  |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/context/\_\_init\_\_.py  |        2 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/context/flow.py          |       34 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/enrollment.py            |       96 |        0 |       24 |        1 |     99% |  170->169 |
| benefits/enrollment/forms.py                 |       14 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/urls.py                  |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/views.py                 |      103 |        2 |       28 |        4 |     95% |37->50, 79, 101->exit, 148 |
| benefits/in\_person/\_\_init\_\_.py          |        0 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/apps.py                  |        4 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/context/\_\_init\_\_.py  |        2 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/context/eligibility.py   |        8 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/forms.py                 |       42 |        0 |        6 |        0 |    100% |           |
| benefits/in\_person/urls.py                  |        6 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/views.py                 |      108 |        0 |       26 |        2 |     99% |60->75, 125->exit |
| benefits/locale/\_\_init\_\_.py              |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/en/\_\_init\_\_.py           |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/en/formats.py                |        1 |        0 |        0 |        0 |    100% |           |
| benefits/locale/es/\_\_init\_\_.py           |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/es/formats.py                |        1 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/\_\_init\_\_.py               |        0 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/analytics.py                  |       41 |       11 |        4 |        0 |     76% |30, 37, 53, 60-61, 66, 71, 76, 81, 86, 91 |
| benefits/oauth/apps.py                       |        5 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/hooks.py                      |       54 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/middleware.py                 |       23 |        0 |        6 |        0 |    100% |           |
| benefits/oauth/urls.py                       |       12 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/views.py                      |       12 |        0 |        0 |        0 |    100% |           |
| benefits/routes.py                           |       98 |        0 |        0 |        0 |    100% |           |
| benefits/secrets.py                          |       48 |        8 |       10 |        1 |     81% |     90-99 |
| benefits/sentry.py                           |       57 |       12 |       10 |        1 |     81% |19, 24-25, 30, 34-35, 63-64, 87-108 |
| benefits/settings.py                         |      131 |        7 |       24 |        9 |     90% |104, 125->130, 141->144, 160, 313, 325, 327, 342, 354 |
| benefits/urls.py                             |       27 |        7 |        4 |        2 |     71% |33->44, 48-62 |
| benefits/wsgi.py                             |        4 |        4 |        0 |        0 |      0% |     10-17 |
|                                    **TOTAL** | **2431** |  **122** |  **462** |   **55** | **93%** |           |


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