FROM ghcr.io/cal-itp/docker-python-web:main

# upgrade pip
RUN python -m pip install --upgrade pip

# overwrite default nginx.conf
COPY appcontainer/nginx.conf /etc/nginx/nginx.conf
COPY appcontainer/proxy.conf /calitp/run/proxy.conf

# copy files needed for version metadata
COPY .git .git

# copy source files
COPY manage.py manage.py
COPY bin bin
COPY benefits benefits
COPY pyproject.toml pyproject.toml

RUN pip install -e .

# ensure $USER can compile messages in the locale directories
USER root
RUN chmod -R 777 benefits/locale
USER $USER

# configure container executable
ENTRYPOINT ["/bin/bash"]
CMD ["bin/start.sh"]
