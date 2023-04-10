FROM benefits_client:latest

# install devcontainer requirements
RUN pip install -e .[dev]

# docs requirements are in a separate file for the GitHub Action
COPY docs/requirements.txt docs/requirements.txt
RUN pip install -r docs/requirements.txt

# install pre-commit environments in throwaway Git repository
# https://stackoverflow.com/a/68758943
COPY .pre-commit-config.yaml .
RUN git init . && \
    pre-commit install-hooks && \
    rm -rf .git
