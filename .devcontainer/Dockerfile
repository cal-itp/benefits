FROM benefits_client:latest

# install Azure CLI
# https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt
USER root
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# install webp CLI
# https://developers.google.com/speed/webp/download
RUN apt install webp -y

USER $USER

COPY . .
# install devcontainer requirements
# this RUN command uses pipcache; this layer is rebuilt if 'COPY . .' changes,
# but pip will use its cache for downloads
RUN --mount=type=cache,id=pipcache,target=${HOME}/.cache/pip pip install -e .[dev,test]

# docs requirements are in a separate file for the GitHub Action
# this RUN command uses pipcache, pip will use its cache for downloads
RUN --mount=type=cache,id=pipcache,target=${HOME}/.cache/pip pip install -r docs/requirements.txt
