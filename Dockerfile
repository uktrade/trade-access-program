FROM python:3.8.3 AS base

WORKDIR /app
ENV PYTHONPATH=/app:$PYTHONPATH

RUN pip install --upgrade pip

# Copy requirements file in separately to rest of project.
# This allows docker to cache requirements, and so only changes to
# requirements.txt will trigger a new pip install
ADD requirements/*.txt /requirements/
RUN pip install -r /requirements/dev.txt

ADD . /app
