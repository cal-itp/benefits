FROM benefits_client:latest

USER root

# install Linux CLI tools for development
RUN apt-get install -qq curl jq ssh

USER $USER

RUN python -m pip install --upgrade pip && \
    pip install black djlint flake8 pre-commit

COPY docs/requirements.txt docs/requirements.txt
RUN pip install -r docs/requirements.txt

COPY tests/pytest/requirements.txt tests/pytest/requirements.txt
RUN pip install -r tests/pytest/requirements.txt

# install pre-commit environments in throwaway Git repository
# https://stackoverflow.com/a/68758943
COPY .pre-commit-config.yaml .
RUN git init . && \
    pre-commit install-hooks && \
    rm -rf .git
