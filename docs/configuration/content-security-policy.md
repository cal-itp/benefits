# Configuring the Content Security Policy

!!! tldr "MDN docs"

    The Mozilla Developer Network has more on [Content Security Policy][mdn-csp]

> The HTTP `Content-Security-Policy` response header allows web site administrators to control resources the user agent is
> allowed to load for a given page.

> With a few exceptions, policies mostly involve specifying server origins and script endpoints. This helps guard against
> cross-site scripting attacks

## `django-csp`

!!! tldr "django-csp docs"

    [Configuring `django-csp`][django-csp-config]

Benefits uses the open source `django-csp` library for helping to configure the correct response headers.

## Environment Variables

### `DJANGO_CSP_CONNECT_SRC`

Comma-separated list of URIs. Configures the [`connect-src`][mdn-csp-connect-src] Content Security Policy directive.

### `DJANGO_CSP_FONT_SRC`

Comma-separated list of URIs. Configures the [`font-src`][mdn-csp-font-src] Content Security Policy directive.

### `DJANGO_CSP_FRAME_SRC`

Comma-separated list of URIs. Configures the [`frame-src`][mdn-csp-frame-src] Content Security Policy directive.

### `DJANGO_CSP_SCRIPT_SRC`

Comma-separated list of URIs. Configures the [`script-src`][mdn-csp-script-src] Content Security Policy directive.

### `DJANGO_CSP_STYLE_SRC`

Comma-separated list of URIs. Configures the [`style-src`][mdn-csp-style-src] Content Security Policy directive.

[django-csp-config]: https://django-csp.readthedocs.io/en/latest/configuration.html#configuring-django-csp
[mdn-csp]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy
[mdn-csp-connect-src]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/connect-src
[mdn-csp-font-src]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/font-src
[mdn-csp-frame-src]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/frame-src
[mdn-csp-script-src]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/script-src
[mdn-csp-style-src]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/style-src
