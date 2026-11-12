# https://playwright.dev/docs/docker
# version needs to match the requirements.txt file
FROM mcr.microsoft.com/playwright/python:v1.65.1-resolute

WORKDIR /playwright

COPY tests/playwright/requirements.txt requirements.txt

RUN python -m pip install --upgrade pip && \
   pip install -r requirements.txt

USER pwuser
