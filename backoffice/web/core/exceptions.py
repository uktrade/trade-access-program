from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class DnbServiceClientException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('Could not communicate with dnb-service.')
    default_code = 'error'


class CompaniesHouseApiException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('Could not communicate with companies house api.')
    default_code = 'error'
