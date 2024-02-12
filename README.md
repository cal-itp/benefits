# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/cal-itp/benefits/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                 |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| benefits/\_\_init\_\_.py             |        6 |        2 |        0 |        0 |     67% |       5-7 |
| benefits/core/\_\_init\_\_.py        |        0 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin.py               |       24 |       24 |        6 |        0 |      0% |      5-44 |
| benefits/core/analytics.py           |       89 |       20 |       18 |        3 |     67% |115-117, 122, 128-150, 161 |
| benefits/core/apps.py                |        5 |        0 |        0 |        0 |    100% |           |
| benefits/core/context\_processors.py |       30 |        2 |       10 |        1 |     92% |    64, 74 |
| benefits/core/middleware.py          |       91 |        5 |       22 |        3 |     93% |38-39, 58-59, 78->83, 146 |
| benefits/core/models.py              |      198 |        3 |       54 |        1 |     98% |73-74, 168 |
| benefits/core/recaptcha.py           |       13 |        5 |        6 |        1 |     58% |     26-32 |
| benefits/core/session.py             |      153 |        2 |       32 |        0 |     99% |     52-53 |
| benefits/core/urls.py                |       24 |        0 |        2 |        0 |    100% |           |
| benefits/core/views.py               |       52 |        0 |       32 |        0 |    100% |           |
| benefits/core/widgets.py             |       25 |        1 |        6 |        3 |     87% |17, 18->exit, 40->43 |
| benefits/eligibility/\_\_init\_\_.py |        0 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/analytics.py    |       30 |        4 |        4 |        2 |     82% |22, 38->40, 40->exit, 46, 56, 61 |
| benefits/eligibility/apps.py         |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/forms.py        |       54 |        8 |       16 |        6 |     80% |39, 116, 118, 120, 130, 136, 143, 166 |
| benefits/eligibility/urls.py         |        4 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/verify.py       |       15 |        0 |        6 |        0 |    100% |           |
| benefits/eligibility/views.py        |      104 |        2 |       58 |        3 |     97% |42, 66, 124->exit |
| benefits/enrollment/\_\_init\_\_.py  |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/analytics.py     |       14 |        2 |        4 |        2 |     78% |13->15, 16, 31 |
| benefits/enrollment/api.py           |      166 |        6 |       54 |        0 |     95% |121-122, 134-135, 147-148 |
| benefits/enrollment/apps.py          |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/forms.py         |       12 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/urls.py          |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/views.py         |       69 |        0 |       26 |        0 |    100% |           |
| benefits/oauth/\_\_init\_\_.py       |        0 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/analytics.py          |       33 |       11 |        2 |        0 |     69% |22, 29, 36, 43, 50-51, 56, 61, 66, 71, 76 |
| benefits/oauth/apps.py               |       11 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/client.py             |       21 |        0 |        4 |        0 |    100% |           |
| benefits/oauth/middleware.py         |       13 |        0 |        4 |        0 |    100% |           |
| benefits/oauth/redirects.py          |       14 |        0 |        2 |        0 |    100% |           |
| benefits/oauth/urls.py               |        4 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/views.py              |       73 |        0 |       26 |        0 |    100% |           |
| benefits/secrets.py                  |       47 |        8 |       10 |        1 |     81% |     83-92 |
| benefits/sentry.py                   |       57 |       12 |       14 |        1 |     79% |19, 24-25, 30, 34-35, 63-64, 87-108 |
| benefits/settings.py                 |      127 |       20 |       32 |       12 |     80% |58-73, 97, 105, 126->131, 142->145, 158, 166, 199, 315, 317, 332, 344 |
| benefits/urls.py                     |       24 |       11 |        4 |        2 |     54% |33-47, 51-55 |
| benefits/wsgi.py                     |        4 |        4 |        0 |        0 |      0% |     10-17 |
|                            **TOTAL** | **1620** |  **152** |  **454** |   **41** | **89%** |           |


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