FROM benefits_client:latest

# install Azure CLI
# https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt
USER root
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# install webp CLI
# https://developers.google.com/speed/webp/download
RUN apt install webp -y

USER $USER

# copy only minimal files needed for dev dependency installs
COPY .git .git
COPY pyproject.toml pyproject.toml

# this RUN command uses pipcache
# setting uid,gid here is critical, as otherwise the Buildkit cache is mounted as root
# even though we are running in the context of non-root $USER
RUN --mount=type=cache,id=pipcache,target=${PIP_CACHE_DIR},uid=${USER_UID},gid=${USER_GID} \
     pip install -e .[dev,test]

# docs requirements are in a separate file for the GitHub Action
COPY docs/requirements.txt docs/requirements.txt
# this RUN command uses pipcache
# setting uid,gid here is critical, as otherwise the Buildkit cache is mounted as root
# even though we are running in the context of non-root $USER
RUN --mount=type=cache,id=pipcache,target=${PIP_CACHE_DIR},uid=${USER_UID},gid=${USER_GID} \
    pip install -r docs/requirements.txt
