FROM benefits_client:latest

USER root

# install Cypress prereqs and other dev tooling
RUN apt-get install -qq libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev \
    libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb curl git jq ssh

USER $USER

RUN python -m pip install --upgrade pip && \
    pip install black flake8 pre-commit

COPY docs/requirements.txt docs/requirements.txt
RUN pip install -r docs/requirements.txt
