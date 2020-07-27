"""
Django settings for tap project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.urls import reverse_lazy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

VCAP_SERVICES = env.json('VCAP_SERVICES', default={})
VCAP_APPLICATION = env.json('VCAP_APPLICATION', default={})

# Application definition

TAP_APPS = [
    'web.apply',
    'web.core',
    'web.companies',
]

INSTALLED_APPS = [
    'authbroker_client',  # django-staff-sso-client
    'custom_usermodel',  # django-staff-sso-usermodel

    # material
    'material.theme.bluegrey',
    'material',
    'material.frontend',
    'material.admin',

    # viewflow
    'viewflow',
    'viewflow.frontend',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sass_processor',
    'django_filters',
] + TAP_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'authbroker_client.middleware.ProtectAllViewsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_USER_MODEL = 'custom_usermodel.User'
CAN_ELEVATE_SSO_USER_PERMISSIONS = False
CAN_CREATE_TEST_USER = False


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

if 'postgres' in VCAP_SERVICES:
    DATABASE_URL = VCAP_SERVICES['postgres'][0]['credentials']['uri']
    DATABASES = {'default': env.db(default=DATABASE_URL)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('POSTGRES_DB'),
            'USER': env('POSTGRES_USER'),
            'PASSWORD': env('POSTGRES_PASSWORD'),
            'HOST': env('POSTGRES_HOST'),
            'PORT': env.int('POSTGRES_PORT'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, '..', 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '..', 'node_modules/govuk-frontend'),
]

SASS_PROCESSOR_INCLUDE_DIRS = [
    os.path.join(BASE_DIR, '..', 'node_modules'),
]

# authbroker config
AUTHBROKER_URL = env('AUTHBROKER_URL', default=None)
AUTHBROKER_CLIENT_ID = env('AUTHBROKER_CLIENT_ID', default=None)
AUTHBROKER_CLIENT_SECRET = env('AUTHBROKER_CLIENT_SECRET', default=None)
AUTHBROKER_SCOPES = 'read write'

AUTHENTICATION_BACKENDS = [
    'authbroker_client.backends.AuthbrokerBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = reverse_lazy('authbroker_client:login')
LOGIN_REDIRECT_URL = reverse_lazy('viewflow:index')

# https://www.django-rest-framework.org/
REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

DNB_SERVICE_URL = env('DNB_SERVICE_URL', default=None)
DNB_SERVICE_TOKEN = env('DNB_SERVICE_TOKEN', default=None)

MIN_GRANT_VALUE = 500
MAX_GRANT_VALUE = 2500
GRANT_VALUE_DECIMAL_PRECISION = {
    'max_digits': 6,
    'decimal_places': 2,
}
