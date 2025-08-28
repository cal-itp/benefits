# https://playwright.dev/docs/docker
FROM mcr.microsoft.com/playwright/python:v1.55.0-jammy

WORKDIR /playwright

COPY tests/playwright/requirements.txt requirements.txt

RUN python -m pip install --upgrade pip && \
   pip install -r requirements.txt

USER pwuser
