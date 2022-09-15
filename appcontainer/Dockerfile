FROM ghcr.io/cal-itp/docker-python-web:main

USER root

# install gettext for use with Django
RUN apt-get update && \
    apt-get install -qq --no-install-recommends gettext

USER $USER

# install python dependencies
COPY appcontainer/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy Django utility script
COPY manage.py manage.py

# copy source files
COPY bin/ bin/
COPY benefits/ benefits/

# ensure $USER can compile messages in the locale directories and copy migration files from $DJANGO_MIGRATIONS_DIR
USER root
RUN chmod -R 777 benefits/locale
RUN chmod -R 777 benefits/core/migrations
USER $USER

# configure container executable
ENTRYPOINT ["/bin/bash"]
CMD ["bin/start.sh"]
