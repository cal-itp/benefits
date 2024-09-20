# multi-stage build
#
# stage 1: builds the benefits package from source
#          using the git metadata for version info
FROM ghcr.io/cal-itp/docker-python-web:main AS build_wheel

WORKDIR /build

# upgrade pip
RUN python -m pip install --upgrade pip && \
    pip install build

# copy source files
COPY . .
RUN git config --global --add safe.directory /build

# build package
RUN python -m build

# multi-stage build
#
# stage 2: installs the benefits package in a fresh base container
#          using the pre-built package, and copying only needed source
FROM ghcr.io/cal-itp/docker-python-web:main AS appcontainer

# overwrite default nginx.conf
COPY appcontainer/nginx.conf /etc/nginx/nginx.conf
COPY appcontainer/proxy.conf /calitp/run/proxy.conf

# copy runtime files
COPY --from=build_wheel /build/dist /build/dist
COPY manage.py manage.py
COPY bin bin
COPY benefits benefits

# install source as a package
RUN pip install $(find /build/dist -name benefits*.whl)

# ensure $USER can compile messages in the locale directories
USER root
RUN chmod -R 777 benefits/locale
USER $USER

# configure container executable
ENTRYPOINT ["/bin/bash"]
CMD ["bin/start.sh"]
