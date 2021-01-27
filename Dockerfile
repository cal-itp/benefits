FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USER=calitp

    # create $USER and home directory
RUN useradd --create-home --shell /bin/bash $USER && \
    # install nginx
    apt-get update && \
    apt-get install -qq nginx && \
    # setup $USER permissions for nginx
    mkdir -p /var/cache/nginx && \
    chown -R $USER /var/cache/nginx && \
    mkdir -p /var/lib/nginx && \
    chown -R $USER /var/lib/nginx && \
    mkdir -p /var/log/nginx && \
    chown -R $USER /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R $USER /var/run/nginx.pid && \
    # and permissions for Django
    mkdir -p /home/$USER/app && \
    chown -R $USER /home/$USER/app && \
    mkdir -p /var/www/static && \
    chown -R $USER /var/www/static && \
    # and permissions for gunicorn
    mkdir -p /var/log/gunicorn && \
    chown -R $USER /var/log/gunicorn

# overwrite default nginx configs
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/nginx.conf

WORKDIR /home/$USER/app

# install python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy source files
COPY manage.py manage.py
COPY benefits/ benefits/
COPY bin/ bin/
COPY data/ data/

# switch to non-root $USER
USER $USER

# configure container executable
ENTRYPOINT ["/bin/bash", "bin/start.sh"]