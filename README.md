# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/cal-itp/benefits/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                 |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| benefits/\_\_init\_\_.py             |        6 |        2 |        0 |        0 |     67% |       5-7 |
| benefits/admin.py                    |       21 |        0 |        4 |        1 |     96% |    37->48 |
| benefits/apps.py                     |        3 |        0 |        0 |        0 |    100% |           |
| benefits/core/\_\_init\_\_.py        |        0 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin.py               |       39 |        0 |        8 |        1 |     98% | 159->exit |
| benefits/core/analytics.py           |       94 |       20 |       16 |        3 |     70% |125-127, 132, 138-160, 171 |
| benefits/core/apps.py                |        5 |        0 |        0 |        0 |    100% |           |
| benefits/core/context\_processors.py |       41 |        2 |        8 |        1 |     94% |    71, 96 |
| benefits/core/middleware.py          |       91 |        3 |       22 |        2 |     96% |58-59, 78->83, 146 |
| benefits/core/models.py              |      195 |        3 |       58 |        1 |     98% |74-75, 229 |
| benefits/core/recaptcha.py           |       13 |        5 |        4 |        1 |     53% |     26-32 |
| benefits/core/session.py             |      132 |        1 |       34 |        0 |     99% |        52 |
| benefits/core/urls.py                |       25 |        0 |        2 |        0 |    100% |           |
| benefits/core/views.py               |       65 |        0 |       38 |        0 |    100% |           |
| benefits/core/widgets.py             |       25 |        1 |        6 |        3 |     87% |17, 18->exit, 40->43 |
| benefits/eligibility/\_\_init\_\_.py |        0 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/analytics.py    |       31 |        4 |        4 |        2 |     83% |24, 40->42, 42->exit, 48, 58, 63 |
| benefits/eligibility/apps.py         |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/forms.py        |       66 |        2 |       16 |        2 |     95% |   42, 142 |
| benefits/eligibility/urls.py         |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/verify.py       |       16 |        0 |        6 |        0 |    100% |           |
| benefits/eligibility/views.py        |       89 |        1 |       58 |        2 |     98% |48, 105->exit |
| benefits/enrollment/\_\_init\_\_.py  |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/analytics.py     |       21 |        4 |        6 |        3 |     74% |13->15, 16, 24->exit, 35, 40, 45 |
| benefits/enrollment/apps.py          |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/enrollment.py    |       96 |        0 |       28 |        1 |     99% |  170->169 |
| benefits/enrollment/forms.py         |       14 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/urls.py          |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/views.py         |       92 |        1 |       44 |        3 |     97% |36->49, 81->exit, 131 |
| benefits/in\_person/\_\_init\_\_.py  |        0 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/apps.py          |        4 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/forms.py         |       19 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/urls.py          |        6 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/views.py         |       76 |        0 |       24 |        2 |     98% |53->65, 90->exit |
| benefits/locale/\_\_init\_\_.py      |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/en/\_\_init\_\_.py   |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/en/formats.py        |        1 |        0 |        0 |        0 |    100% |           |
| benefits/locale/es/\_\_init\_\_.py   |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/es/formats.py        |        1 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/\_\_init\_\_.py       |        0 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/analytics.py          |       41 |       10 |        4 |        0 |     78% |30, 37, 53, 60-61, 71, 76, 81, 86, 91 |
| benefits/oauth/apps.py               |        5 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/client.py             |       24 |        0 |        4 |        0 |    100% |           |
| benefits/oauth/middleware.py         |       23 |        0 |        6 |        0 |    100% |           |
| benefits/oauth/redirects.py          |       22 |        0 |        2 |        0 |    100% |           |
| benefits/oauth/urls.py               |        5 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/views.py              |      122 |        1 |       42 |        2 |     98% |131->146, 174 |
| benefits/routes.py                   |      106 |        0 |       68 |        0 |    100% |           |
| benefits/secrets.py                  |       48 |        8 |       10 |        1 |     81% |     90-99 |
| benefits/sentry.py                   |       57 |       12 |       14 |        1 |     79% |19, 24-25, 30, 34-35, 63-64, 87-108 |
| benefits/settings.py                 |      121 |        6 |       22 |        8 |     90% |95, 116->121, 132->135, 151, 305, 307, 322, 334 |
| benefits/urls.py                     |       22 |        7 |        2 |        1 |     67% |     35-49 |
| benefits/wsgi.py                     |        4 |        4 |        0 |        0 |      0% |     10-17 |
|                            **TOTAL** | **1907** |   **97** |  **560** |   **41** | **94%** |           |


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