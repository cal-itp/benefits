FROM benefits_client:latest

USER root

# install apt packages using the archives and lists cache
RUN --mount=type=cache,id=apt-archives,sharing=locked,target=/var/cache/apt/archives \
    --mount=type=cache,id=apt-lists,sharing=locked,target=/var/lib/apt/lists \
    # install Azure CLI
    # https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt
    curl -sL https://aka.ms/InstallAzureCLIDeb | bash && \
    # install webp CLI
    # https://developers.google.com/speed/webp/download
    apt install locales webp -y

# VSCode will use en_US for git operations, so make it available in the container
# https://github.com/microsoft/vscode/pull/210506
RUN locale-gen en_US.UTF-8

USER $USER

# copy only minimal files needed for dev dependency installs
COPY .git .git
COPY pyproject.toml pyproject.toml

# this RUN command uses pipcache
# setting uid,gid here is critical, as otherwise the Buildkit cache is mounted as root
# even though we are running in the context of non-root $USER
RUN --mount=type=cache,id=pipcache,target=${PIP_CACHE_DIR},uid=${USER_UID},gid=${USER_GID} \
     pip install --user -e .[dev,test]

# docs requirements are in a separate file for the GitHub Action
COPY docs/requirements.txt docs/requirements.txt
# this RUN command uses pipcache
# setting uid,gid here is critical, as otherwise the Buildkit cache is mounted as root
# even though we are running in the context of non-root $USER
RUN --mount=type=cache,id=pipcache,target=${PIP_CACHE_DIR},uid=${USER_UID},gid=${USER_GID} \
    pip install --user -r docs/requirements.txt
