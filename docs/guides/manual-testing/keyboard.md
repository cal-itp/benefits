# Keyboard testing

Keyboard testing refers to testing the app on a desktop/laptop machine _without_ using a mouse, trackpad, or touchscreen. This is an important
part of manual testing as there are many users that prefer and/or need to primarily or exclusively use a keyboard for online
navigation.

To perform keyboard testing:

- Use <kbd>Tab</kbd> to focus on a button, link, or other UI element.
- Use <kbd>Enter</kbd> select ("click") the focused UI element.

## When to test

- When new UI elements are introduced.
- When significant UI/design changes are introduced (e.g. sit-wide style changes, template refactoring).

## Scenarios

The following scenarios should be reviewed at a minimum.

- The skip nav, a link with the text `Skip to main content` / `Saltar al contenido principal`, should appear on the first tab press on any page.
- All links, buttons, and form elements should have a visible indication that the targeted item is focused.
- All modals should close by pressing <kbd>Escape</kbd>.
