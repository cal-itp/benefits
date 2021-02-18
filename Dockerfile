FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USER=calitp

    # create $USER and home directory
RUN useradd --create-home --shell /bin/bash $USER && \
    # install nginx
    apt-get update && \
    apt-get install -qq --no-install-recommends gettext nginx && \
    # setup $USER permissions for nginx
    mkdir -p /var/cache/nginx && \
    chown -R $USER /var/cache/nginx && \
    mkdir -p /var/lib/nginx && \
    chown -R $USER /var/lib/nginx && \
    mkdir -p /var/log/nginx && \
    chown -R $USER /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R $USER /var/run/nginx.pid && \
    # setup directories and permissions for Django and gunicorn
    mkdir -p /home/$USER/app/run && \
    mkdir -p /home/$USER/app/static && \
    chown -R $USER /home/$USER

# enter app directory
WORKDIR /home/$USER/app

# install python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy source files
COPY manage.py manage.py
COPY benefits/ benefits/
COPY bin/ bin/

# overwrite default nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

# ensure $USER can compile messages in the locale directories
RUN chown -R $USER /home/$USER/app/benefits/locale

# switch to non-root $USER
USER $USER

# configure container executable
ENTRYPOINT ["/bin/bash", "bin/start.sh"]