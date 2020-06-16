#!/usr/bin/env bash

###### RUN ######

wait-for-it -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}"
python manage.py migrate --noinput

case ${DJANGO_SETTINGS_MODULE} in
    "config.settings.local" | "config.settings.test")
        python manage.py runserver "0.0.0.0:8000"
    ;;
    "config.settings.dev" | "config.settings.staging" | "config.settings.prod")
        python manage.py collectstatic --no-input
        gunicorn config.wsgi:application --bind "0.0.0.0:8000" --timeout 300 --log-file
    ;;
    *)
        echo "Bad DJANGO_SETTINGS_MODULE"
        exit 1
esac
