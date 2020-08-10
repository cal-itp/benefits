FROM python:3.9-slim
ENV PYTHONUNBUFFERED 1

EXPOSE 80

USER root

RUN apt-get update && \
    apt-get install -qq gettext nginx

ENV USER=calitp

RUN useradd --create-home --shell /bin/bash $USER

USER $USER
WORKDIR /home/$USER/benefits

ENV PATH=/home/$USER/.local/bin:$PATH

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY manage.py manage.py
COPY benefits/ benefits/
