# Testing translations

The Benefits app is fully internationalized and currently supports native translation in the following languages:

- English
- Spanish

Viewing the Benefits app in multiple languages is an important part of manual testing. The purpose is to ensure there are no
untranslated strings or strange formatting issues introduced by changing the display language. App functionality should remain identical
regardless of the chosen display language.

Use the [Benefits app in the `test` environment](https://test-benefits.calitp.org/) for testing translations, since this environment is both close to `prod` in terms of configuration, and gives you the opportunity to explore all pages and flows using [test credentials](./getting-started.md).

## Switching languages

When viewing the app in English, click the **Español** button on the right side of the application header to switch the display
language to Spanish.

When viewing the app in Spanish, click the **English** button on the right side of the application header to switch the display
language to English.

## When to test

- When new pages and/or UI elements are introduced.
- When significant copy changes are introduced.
- When a new transit agency and/or enrollment flow are introduced.

## Scenarios

The following scenarios should be reviewed at a minimum. Look out for missing translations or formatting issues that only
manifest when the display language is changed.

- Choosing a transit agency.
- Choosing an enrollment pathway.
- Following a **Login.gov** enrollment pathway to completion.
  - Also review when a user _is not eligible_.
- Following a **Medicare.gov** enrollment pathway to completion.
  - Also review when a user _is not eligible_.
- Following an **Agency Card** pathway to completion.
  - Also review when a user _is not eligible_.
- Reviewing the **Help** page (link in the footer).
