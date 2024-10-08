# Basic command (runs Chromium)

pytest -k test_example --headed --slowmo 1000

# (From here, run second test only in the interest of time)

# Use --browser to run with a different browser

# pytest -k test_get_started_link --headed --browser firefox

# Use --device to run with different viewports

# pytest -k test_get_started_link --headed --device "iPhone 13"

# Run in debug mode (https://playwright.dev/python/docs/running-tests#debugging-tests)

# PWDEBUG=1 pytest -s -k test_get_started_link

# More CLI options:
# https://playwright.dev/python/docs/test-runners
# https://playwright.dev/python/docs/running-tests#command-line
