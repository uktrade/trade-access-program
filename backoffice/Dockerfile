FROM python:3.8.8 AS base

RUN apt-get update && apt-get install --assume-yes graphviz

WORKDIR /app
ENV PYTHONPATH=/app:$PYTHONPATH

RUN pip install --upgrade pip

# Copy requirements file in separately to rest of project.
# This allows docker to cache requirements, and so only changes to
# requirements.txt will trigger a new pip install
ADD requirements/*.txt /requirements/
RUN pip install -r /requirements/dev.txt

ADD . /app
