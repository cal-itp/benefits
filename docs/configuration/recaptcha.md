# Configuring reCAPTCHA

!!! tldr "reCAPTCHA docs"

    See the [reCAPTCHA Developer's Guide][recaptcha-intro] for more information

[reCAPTCHA v3][recaptcha] is a free Google-provided service that helps protect the app from spam and abuse by using advanced
risk analysis techniques to tell humans and bots apart.

reCAPTCHA is applied to all forms in the Benefits app that collect user-provided information. Version 3 works silently in the
background, with no additional interaction required by the user.

## Environment variables

!!! warning

    The following environment variables are all required to activate the reCAPTCHA feature

### `DJANGO_RECAPTCHA_API_URL`

URL to the reCAPTCHA JavaScript API library.

E.g. `https://www.google.com/recaptcha/api.js`

### `DJANGO_RECAPTCHA_SITE_KEY`

Site key for the reCAPTCHA configuration.

### `DJANGO_RECAPTCHA_SECRET_KEY`

Secret key for the reCAPTCHA configuration.

### `DJANGO_RECAPTCHA_VERIFY_URL`

!!! tldr "reCAPTCHA docs"

    [Verifying the user's response][recaptcha-verify]

URL for the reCAPTCHA verify service.

E.g. `https://www.google.com/recaptcha/api/siteverify`

[recaptcha]: https://developers.google.com/recaptcha
[recaptcha-intro]: https://developers.google.com/recaptcha/intro
[recaptcha-verify]: https://developers.google.com/recaptcha/docs/verify
