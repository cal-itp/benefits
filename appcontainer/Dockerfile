# multi-stage build
#
# stage 1: builds the benefits package from source
#          using the git metadata for version info
FROM ghcr.io/cal-itp/docker-python-web:main AS build_wheel

WORKDIR /build

# upgrade pip and install build package
# this RUN command benefits from the pipcache for downloading/installing 'build'
# the layer for this command will be cached by Docker if 'pip' and 'build' requirements don't change
RUN --mount=type=cache,id=pipcache,target=${HOME}/.cache/pip python -m pip install --upgrade pip && \
    pip install build

# copy all source files; changes here will invalidate subsequent Docker layers
COPY . .
RUN git config --global --add safe.directory /build

# build the wheel, using pipcache for any build-time dependencies
# this layer is rebuilt if 'COPY . .' changes
RUN --mount=type=cache,id=pipcache,target=${HOME}/.cache/pip python -m build

# multi-stage build
#
# stage 2: installs the benefits package in a fresh base container
#          using the pre-built package, and copying only needed source
FROM ghcr.io/cal-itp/docker-python-web:main AS appcontainer

# overwrite default nginx.conf
COPY appcontainer/nginx.conf /etc/nginx/nginx.conf
COPY appcontainer/proxy.conf /calitp/run/proxy.conf

# copy the wheel built in the previous stage
COPY --from=build_wheel /build/dist /build/dist
# copy runtime files
COPY manage.py manage.py
COPY bin bin
COPY benefits benefits

# install the locally built wheel and its dependencies
# this RUN command uses pipcache; if the wheel file changes (due to code changes),
# this Docker layer will be rebuilt, but pip will use its cache for downloads
RUN --mount=type=cache,id=pipcache,target=${HOME}/.cache/pip pip install $(find /build/dist -name benefits*.whl)

USER root
COPY LICENSE LICENSE
#ensure $USER can compile messages in the locale directories
RUN chmod -R 777 benefits/locale
USER $USER

# configure container executable
ENTRYPOINT ["/bin/bash"]
CMD ["bin/start.sh"]
