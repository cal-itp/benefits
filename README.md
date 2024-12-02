# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/cal-itp/benefits/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                 |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| benefits/\_\_init\_\_.py             |        6 |        2 |        0 |        0 |     67% |       5-7 |
| benefits/admin.py                    |       24 |        0 |        4 |        1 |     96% |    41->53 |
| benefits/apps.py                     |        3 |        0 |        0 |        0 |    100% |           |
| benefits/core/\_\_init\_\_.py        |        0 |        0 |        0 |        0 |    100% |           |
| benefits/core/admin.py               |       43 |        0 |        8 |        1 |     98% | 200->exit |
| benefits/core/analytics.py           |       99 |       20 |       18 |        3 |     72% |136-138, 143, 149-171, 182 |
| benefits/core/apps.py                |        5 |        0 |        0 |        0 |    100% |           |
| benefits/core/context\_processors.py |       44 |        2 |       10 |        2 |     93% |28->36, 81, 106 |
| benefits/core/middleware.py          |       91 |        3 |       22 |        2 |     96% |58-59, 78->83, 146 |
| benefits/core/models.py              |      327 |        3 |       74 |        2 |     99% |97-98, 331->339, 542 |
| benefits/core/recaptcha.py           |       13 |        5 |        4 |        1 |     53% |     26-32 |
| benefits/core/session.py             |      141 |        1 |       38 |        0 |     99% |        52 |
| benefits/core/urls.py                |       25 |        0 |        2 |        0 |    100% |           |
| benefits/core/views.py               |       65 |        0 |        2 |        0 |    100% |           |
| benefits/core/widgets.py             |       25 |        1 |        6 |        3 |     87% |17, 18->exit, 40->43 |
| benefits/eligibility/\_\_init\_\_.py |        0 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/analytics.py    |       27 |        4 |        2 |        1 |     83% |21, 39->exit, 45, 55, 60 |
| benefits/eligibility/apps.py         |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/forms.py        |       66 |        2 |       16 |        2 |     95% |   42, 142 |
| benefits/eligibility/urls.py         |        5 |        0 |        0 |        0 |    100% |           |
| benefits/eligibility/verify.py       |       16 |        0 |        6 |        0 |    100% |           |
| benefits/eligibility/views.py        |       89 |        1 |       24 |        2 |     97% |48, 105->exit |
| benefits/enrollment/\_\_init\_\_.py  |        0 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/analytics.py     |       21 |        4 |        6 |        3 |     74% |21->23, 24, 32->exit, 43, 48, 61 |
| benefits/enrollment/apps.py          |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/enrollment.py    |       96 |        0 |       24 |        1 |     99% |  170->169 |
| benefits/enrollment/forms.py         |       14 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/urls.py          |        5 |        0 |        0 |        0 |    100% |           |
| benefits/enrollment/views.py         |      102 |        2 |       28 |        4 |     95% |37->50, 79, 101->exit, 152 |
| benefits/in\_person/\_\_init\_\_.py  |        0 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/apps.py          |        4 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/forms.py         |       21 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/urls.py          |        6 |        0 |        0 |        0 |    100% |           |
| benefits/in\_person/views.py         |      107 |        0 |       26 |        2 |     98% |60->75, 125->exit |
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
| benefits/oauth/views.py              |      123 |        1 |       32 |        3 |     97% |131->147, 144->135, 175 |
| benefits/routes.py                   |      106 |        0 |        0 |        0 |    100% |           |
| benefits/secrets.py                  |       48 |        8 |       10 |        1 |     81% |     90-99 |
| benefits/sentry.py                   |       57 |       12 |       10 |        1 |     81% |19, 24-25, 30, 34-35, 63-64, 87-108 |
| benefits/settings.py                 |      129 |        6 |       22 |        8 |     91% |103, 124->129, 140->143, 159, 322, 324, 339, 351 |
| benefits/urls.py                     |       24 |        8 |        2 |        1 |     65% |     36-54 |
| benefits/wsgi.py                     |        4 |        4 |        0 |        0 |      0% |     10-17 |
|                            **TOTAL** | **2113** |   **99** |  **412** |   **44** | **94%** |           |


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