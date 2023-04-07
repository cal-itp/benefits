FROM benefits_client:latest

# install devcontainer requirements
COPY .devcontainer/requirements.txt .devcontainer/requirements.txt
RUN pip install -r .devcontainer/requirements.txt

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
