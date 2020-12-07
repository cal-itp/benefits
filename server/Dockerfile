FROM python:3.8
ENV PYTHONUNBUFFERED 1

EXPOSE 5000

WORKDIR /usr/src/server

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
