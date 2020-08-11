from rest_framework import serializers

from web.companies.models import Company


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ['dnb_service_duns_number', 'name', 'grantapplication_set']
