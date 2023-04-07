FROM ghcr.io/cal-itp/docker-python-web:main

# install python dependencies
COPY appcontainer/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy Django utility script
COPY manage.py manage.py

# copy source files
COPY bin/ bin/
COPY benefits/ benefits/

# ensure $USER can compile messages in the locale directories
USER root
RUN chmod -R 777 benefits/locale
USER $USER

# configure container executable
ENTRYPOINT ["/bin/bash"]
CMD ["bin/start.sh"]
