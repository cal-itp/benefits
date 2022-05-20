FROM benefits_client:latest

USER root

# install node.js
# see https://github.com/nodesource/distributions#installation-instructions

RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash

RUN apt-get install -qq nodejs npm libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev \
    libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb curl jq ssh

USER $USER

RUN python -m pip install --upgrade pip && \
    pip install black flake8 pre-commit

COPY docs/requirements.txt docs/requirements.txt
RUN pip install -r docs/requirements.txt

COPY tests/pytest/requirements.txt tests/pytest/requirements.txt
RUN pip install -r tests/pytest/requirements.txt
