# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/cal-itp/benefits/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                 |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| benefits/\_\_init\_\_.py             |        6 |        2 |        0 |        0 |     67% |       5-7 |
| benefits/core/\_\_init\_\_.py        |        0 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin.py               |        9 |        9 |        4 |        0 |      0% |      4-22 |
| benefits/core/analytics.py           |       89 |       20 |       18 |        3 |     67% |114-116, 121, 127-149, 160 |
| benefits/core/apps.py                |        5 |        0 |        0 |        0 |    100% |           |
| benefits/core/context\_processors.py |       30 |        2 |       10 |        1 |     92% |    63, 73 |
| benefits/core/middleware.py          |       91 |        5 |       22 |        3 |     93% |37-38, 57-58, 77->82, 145 |
| benefits/core/models.py              |      176 |        0 |       48 |        1 |     99% |    35->38 |
| benefits/core/recaptcha.py           |       13 |        5 |        6 |        1 |     58% |     25-31 |
| benefits/core/session.py             |      153 |        2 |       32 |        0 |     99% |     51-52 |
| benefits/core/urls.py                |       24 |        0 |        2 |        0 |    100% |           |
| benefits/core/views.py               |       52 |        0 |       32 |        0 |    100% |           |
| benefits/core/widgets.py             |       25 |        1 |        6 |        3 |     87% |16, 17->exit, 39->42 |
| benefits/eligibility/\_\_init\_\_.py |        0 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/analytics.py    |       30 |        4 |        4 |        2 |     82% |21, 37->39, 39->exit, 45, 55, 60 |
| benefits/eligibility/apps.py         |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/forms.py        |       51 |        7 |       16 |        6 |     81% |38, 115, 117, 119, 129, 135, 142 |
| benefits/eligibility/urls.py         |        4 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/verify.py       |       15 |        0 |        6 |        0 |    100% |           |
| benefits/eligibility/views.py        |      104 |        2 |       58 |        3 |     97% |41, 65, 123->exit |
| benefits/enrollment/\_\_init\_\_.py  |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/analytics.py     |       14 |        2 |        4 |        2 |     78% |12->14, 15, 30 |
| benefits/enrollment/api.py           |      166 |        6 |       54 |        0 |     95% |126-127, 139-140, 152-153 |
| benefits/enrollment/apps.py          |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/forms.py         |       12 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/urls.py          |        4 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/views.py         |       69 |        0 |       26 |        0 |    100% |           |
| benefits/oauth/\_\_init\_\_.py       |        0 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/analytics.py          |       33 |       11 |        2 |        0 |     69% |21, 28, 35, 42, 49-50, 55, 60, 65, 70, 75 |
| benefits/oauth/apps.py               |       11 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/client.py             |       21 |        0 |        4 |        0 |    100% |           |
| benefits/oauth/middleware.py         |       13 |        0 |        4 |        0 |    100% |           |
| benefits/oauth/redirects.py          |       14 |        0 |        2 |        0 |    100% |           |
| benefits/oauth/urls.py               |        4 |        0 |        0 |        0 |    100% |           |
| benefits/oauth/views.py              |       73 |        0 |       26 |        0 |    100% |           |
| benefits/sentry.py                   |       56 |       12 |       14 |        1 |     79% |19, 24-25, 30, 34-35, 63-64, 85-106 |
| benefits/settings.py                 |      108 |       10 |       26 |       12 |     84% |39, 62, 70, 91->96, 107->110, 123, 131, 164, 281, 283, 294, 304 |
| benefits/urls.py                     |       18 |        6 |        4 |        2 |     64% |31-34, 37-40 |
| benefits/wsgi.py                     |        4 |        4 |        0 |        0 |      0% |      9-16 |
|                            **TOTAL** | **1507** |  **110** |  **430** |   **40** | **91%** |           |


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