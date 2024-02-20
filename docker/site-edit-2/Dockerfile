# syntax=docker/dockerfile:1
# https://docs.docker.com/samples/django/
FROM python:3.12
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
RUN apt-get update \
    && apt-get -y install libpq-dev gcc build-essential
COPY . /code/
RUN mkdir /emlo_home
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt