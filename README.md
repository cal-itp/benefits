# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/cal-itp/benefits/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                 |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| benefits/\_\_init\_\_.py             |        6 |        2 |        0 |        0 |     67% |       5-7 |
| benefits/core/\_\_init\_\_.py        |        0 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin.py               |       28 |        0 |        6 |        0 |    100% |           |
| benefits/core/analytics.py           |       96 |       20 |       16 |        3 |     71% |127-129, 134, 140-162, 173 |
| benefits/core/apps.py                |        5 |        0 |        0 |        0 |    100% |           |
| benefits/core/context\_processors.py |       38 |        2 |        8 |        1 |     93% |    69, 94 |
| benefits/core/middleware.py          |       91 |        5 |       22 |        3 |     93% |38-39, 58-59, 78->83, 146 |
| benefits/core/models.py              |      225 |        3 |       66 |        1 |     99% |72-73, 201 |
| benefits/core/recaptcha.py           |       13 |        5 |        4 |        1 |     53% |     26-32 |
| benefits/core/session.py             |      142 |        1 |       40 |        0 |     99% |        51 |
| benefits/core/urls.py                |       24 |        0 |        2 |        0 |    100% |           |
| benefits/core/views.py               |       53 |        0 |       32 |        0 |    100% |           |
| benefits/core/widgets.py             |       25 |        1 |        6 |        3 |     87% |17, 18->exit, 40->43 |
| benefits/eligibility/\_\_init\_\_.py |        0 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/analytics.py    |       30 |        4 |        4 |        2 |     82% |22, 38->40, 40->exit, 46, 56, 61 |
| benefits/eligibility/apps.py         |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/forms.py        |       62 |        2 |       16 |        2 |     95% |   41, 141 |
| benefits/eligibility/urls.py         |        4 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/verify.py       |       15 |        0 |        6 |        0 |    100% |           |
| benefits/eligibility/views.py        |      104 |        2 |       58 |        3 |     97% |41, 65, 124->exit |
| benefits/enrollment/\_\_init\_\_.py  |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/analytics.py     |       21 |        4 |        6 |        3 |     74% |13->15, 16, 24->exit, 35, 40, 45 |
| benefits/enrollment/apps.py          |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/forms.py         |       12 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/urls.py          |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/views.py         |      153 |        1 |       56 |        2 |     99% |211->210, 250 |
| benefits/locale/\_\_init\_\_.py      |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/en/\_\_init\_\_.py   |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/en/formats.py        |        1 |        0 |        0 |        0 |    100% |           |
| benefits/locale/es/\_\_init\_\_.py   |        0 |        0 |        0 |        0 |    100% |           |
| benefits/locale/es/formats.py        |        1 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/\_\_init\_\_.py       |        0 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/analytics.py          |       35 |       10 |        4 |        0 |     74% |22, 29, 45, 52-53, 58, 63, 68, 73, 78 |
| benefits/oauth/apps.py               |        5 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/client.py             |       23 |        0 |        4 |        0 |    100% |           |
| benefits/oauth/middleware.py         |       13 |        0 |        4 |        0 |    100% |           |
| benefits/oauth/redirects.py          |       14 |        0 |        2 |        0 |    100% |           |
| benefits/oauth/urls.py               |        4 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/views.py              |       77 |        0 |       28 |        1 |     99% |    70->85 |
| benefits/secrets.py                  |       48 |        8 |       10 |        1 |     81% |     90-99 |
| benefits/sentry.py                   |       57 |       12 |       14 |        1 |     79% |19, 24-25, 30, 34-35, 63-64, 87-108 |
| benefits/settings.py                 |      119 |        6 |       22 |        8 |     90% |92, 113->118, 129->132, 147, 301, 303, 318, 330 |
| benefits/urls.py                     |       22 |        7 |        2 |        1 |     67% |     34-48 |
| benefits/wsgi.py                     |        4 |        4 |        0 |        0 |      0% |     10-17 |
|                            **TOTAL** | **1584** |   **99** |  **438** |   **36** | **93%** |           |


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