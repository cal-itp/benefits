# declare default build args for later stages
ARG PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USER=calitp \
    USER_UID=1000 \
    USER_GID=1000

# multi-stage build
#
# stage 1: builds the benefits package from source
#          using the git metadata for version info
FROM ghcr.io/cal-itp/docker-python-web:main AS build_wheel

# renew top-level args in this stage
ARG PYTHONDONTWRITEBYTECODE \
    PYTHONUNBUFFERED \
    USER \
    USER_UID \
    USER_GID

# set env vars for the user, including HOME
ENV PYTHONUNBUFFERED=${PYTHONUNBUFFERED} \
    PYTHONDONTWRITEBYTECODE=${PYTHONDONTWRITEBYTECODE} \
    HOME=/home/${USER} \
    USER=${USER} \
    PATH="/home/${USER}/.local/bin:$PATH" \
    # update env for local pip installs
    # see https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUSERBASE
    # since all `pip install` commands are in the context of $USER
    # $PYTHONUSERBASE is the location used by default
    PYTHONUSERBASE="/home/${USER}/.local" \
    # where to store the pip cache (use the default)
    # https://pip.pypa.io/en/stable/cli/pip/#cmdoption-cache-dir
    PIP_CACHE_DIR="/home/${USER}/.cache/pip"

WORKDIR /build

# upgrade pip and install build package
# this RUN command benefits from the pipcache for downloading/installing 'build'
# the layer for this command will be cached by Docker if 'pip' and 'build' requirements don't change
RUN --mount=type=cache,id=pipcache,target=${PIP_CACHE_DIR},uid=${USER_UID},gid=${USER_GID} \
    python -m pip install --user --upgrade pip && \
    pip install --user build

# copy all source files; changes here will invalidate subsequent Docker layers
COPY . .
RUN git config --global --add safe.directory /build

# build the wheel, using pipcache for any build-time dependencies
# this layer is rebuilt if 'COPY . .' changes
RUN --mount=type=cache,id=pipcache,target=${PIP_CACHE_DIR},uid=${USER_UID},gid=${USER_GID} \
    python -m build

# multi-stage build
#
# stage 2: installs the benefits package in a fresh base container
#          using the pre-built package, and copying only needed source
FROM ghcr.io/cal-itp/docker-python-web:main AS appcontainer

# renew top-level args in this stage
ARG PYTHONDONTWRITEBYTECODE \
    PYTHONUNBUFFERED \
    USER \
    USER_UID \
    USER_GID

# set env vars from args so they persist into running containers
ENV PYTHONUNBUFFERED=${PYTHONUNBUFFERED} \
    PYTHONDONTWRITEBYTECODE=${PYTHONDONTWRITEBYTECODE} \
    HOME=/home/${USER} \
    USER=${USER} \
    USER_UID=${USER_UID} \
    USER_GID=${USER_GID} \
    PATH="/home/${USER}/.local/bin:$PATH" \
    # update env for local pip installs
    # see https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUSERBASE
    # since all `pip install` commands are in the context of $USER
    # $PYTHONUSERBASE is the location used by default
    PYTHONUSERBASE="/home/${USER}/.local" \
    # where to store the pip cache (use the default)
    # https://pip.pypa.io/en/stable/cli/pip/#cmdoption-cache-dir
    PIP_CACHE_DIR="/home/${USER}/.cache/pip"

USER $USER

# copy mostly-static runtime files
COPY LICENSE LICENSE
COPY manage.py manage.py
# overwrite default nginx.conf
COPY appcontainer/nginx.conf /etc/nginx/nginx.conf
COPY appcontainer/proxy.conf /calitp/run/proxy.conf

# copy runtime files
COPY bin bin
COPY benefits benefits

#ensure $USER can compile messages in the locale directories
USER root
RUN chown -R $USER:$USER benefits
USER $USER

# copy the wheel built in the previous stage
COPY --from=build_wheel /build/dist /build/dist

# install the locally built wheel and its dependencies
# this RUN command uses pipcache; if the wheel file changes (due to code changes),
# this Docker layer will be rebuilt, but pip will use its cache for downloads
RUN --mount=type=cache,id=pipcache,target=${PIP_CACHE_DIR},uid=${USER_UID},gid=${USER_GID} \
    python -m pip install --user --upgrade pip && \
    pip install $(find /build/dist -name benefits*.whl)

# configure container executable
ENTRYPOINT ["/bin/bash"]
CMD ["bin/start.sh"]
