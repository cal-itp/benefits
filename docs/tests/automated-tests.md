# Automated tests

## Pytest

The tests done at a request/unit level are run via [pytest-django](https://pytest-django.readthedocs.io/en/latest/index.html).

To run locally, start the [Devcontainer](../development/README.md) and run:

```bash
tests/pytest/run.sh
```

The helper script:

1. Runs the tests with `pytest`
2. Calculates test coverage with [`coverage`](https://coverage.readthedocs.io/en/latest/)
3. Generates a `coverage` report in HTML in the app's `static/` directory

The report can be viewed by launching the app and navigating to `http://localhost:$DJANGO_LOCAL_PORT/static/coverage/index.html`

The report files include a local `.gitignore` file, so the entire directory is hidden from source control.

### Latest coverage report

We also make the latest (from `main`) coverage report available online here: [Coverage report](../coverage)

## Playwright

For testing the app flows from beginning to end, we use Playwright.

To run all Playwright tests locally, open a terminal outside the devcontainer and run:

```bash
docker compose run --rm playwright
```

### Running in headed mode

To run Playwright in headed mode, you need to enable X11 forwarding.

Some steps are required for macOS and Windows to check that you have an X Server.

#### macOS

macOS doesn't provide a built-in X Server, so you'll need to install XQuartz which will provide one:

- Install XQuartz: `brew install --cask xquartz`
- Open XQuartz, go to Preferences -> Security, and check “Allow connections from network clients”
- Restart your computer (restarting XQuartz might not be enough)
- Start XQuartz with `xhost +localhost`

#### Windows

Windows provides an X Server as a part of Windows Subsystem for Linux (WSL).

To verify that WSL and WSL GUI are installed and running:

- Launch WSL from the Start Menu
- In the Linux terminal that opens, verify that the directory `/mnt/wslg` exists by running:

  ```bash
  ls -a -w 1 /mnt/wslg
  ```

  and that it contains these files:

  ```
  .
  ..
  .X11-unix
  PulseAudioRDPSink
  PulseAudioRDPSource
  PulseServer
  distro
  doc
  dumps
  pulseaudio.log
  runtime-dir
  stderr.log
  versions.txt
  weston.log
  wlog.log
  ```

If you don't see WSL in the Start Menu or the `ls` command fails, you need to install WSL.

#### Set `DISPLAY` environment variable

In your `.env` file, set `DISPLAY` to the value for your operating system:

- macOS: `host.docker.internal:0`
- Linux: `$DISPLAY`
- Windows: `:0`

For example, for macOS, you'd add this line to your `.env` file:

```
DISPLAY=host.docker.internal:0
```

!!! info

    The steps above are adapted from [https://www.oddbird.net/2022/11/30/headed-playwright-in-docker/](https://www.oddbird.net/2022/11/30/headed-playwright-in-docker/).

#### Run all tests in headed mode

In `tests/playwright/pytest.ini`, add `--headed` to `addopts`, and run all tests with the same command as before:

```bash
docker compose run --rm playwright
```

#### Use Playwright GUI tools

Start a bash session inside the `playwright` container:

```bash
docker compose run --rm playwright /bin/bash
```

From here, you can use the `playwright` CLI and any of the GUI tools it provides. Run `playwright --help` to see different commands you can run.

For example, to launch a Chrome window with a Playwright Inspector attached to it, run:

```bash
playwright cr
```

![Screenshot showing a Chrome window with Playwright Inspector attached to it](img/playwright-inspector.png)
