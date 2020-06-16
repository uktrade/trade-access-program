FROM python:3.8.3 AS base

RUN apt-get update -y && apt-get install -y wait-for-it

WORKDIR /app
ENV PYTHONPATH=/app:$PYTHONPATH

RUN pip install --upgrade pip

# Copy requirements file in separately to rest of project.
# This allows docker to cache requirements, and so only changes to
# requirements.txt will trigger a new pip install
ADD requirements/*.txt /requirements/
RUN pip install -r /requirements/extra.txt

ADD . /app

CMD [ "/app/scripts/django-startup.sh" ]
