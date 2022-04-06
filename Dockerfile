FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USER=calitp

# create non-root $USER and home directory
RUN useradd --create-home --shell /bin/bash $USER && \
    # setup $USER permissions for nginx
    mkdir -p /var/cache/nginx && \
    chown -R $USER /var/cache/nginx && \
    mkdir -p /var/lib/nginx && \
    chown -R $USER /var/lib/nginx && \
    mkdir -p /var/log/nginx && \
    chown -R $USER /var/log/nginx && \
    touch /var/log/nginx/error.log && \
    chown $USER /var/log/nginx/error.log && \
    touch /var/run/nginx.pid && \
    chown -R $USER /var/run/nginx.pid && \
    # setup directories and permissions for Django and gunicorn
    mkdir -p /home/$USER/app/config && \
    mkdir -p /home/$USER/app/run && \
    mkdir -p /home/$USER/app/static && \
    chown -R $USER /home/$USER && \
    # install server components, nodejs
    # see https://github.com/nodesource/distributions#installation-instructions
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash && \
    apt-get update && \
    apt-get install -qq --no-install-recommends gettext nginx nodejs npm

# enter app directory
WORKDIR /home/$USER/app

# copy config files
COPY gunicorn.conf.py gunicorn.conf.py
COPY manage.py manage.py

# overwrite default nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

# copy source files
COPY bin/ bin/
COPY benefits/ benefits/

# ensure $USER can compile messages and copy static files
RUN chmod -R 777 benefits/locale benefits/static

# switch to non-root $USER
USER $USER

# install node dependencies
COPY package*.json .
RUN npm ci && cp node_modules/oidc-client-ts/dist/browser/oidc-client-ts* benefits/static/js

# update PATH for local pip installs
ENV PATH "$PATH:/home/$USER/.local/bin"

# install python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# configure container executable
ENTRYPOINT ["/bin/bash"]
CMD ["bin/start.sh"]
