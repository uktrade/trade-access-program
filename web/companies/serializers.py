from rest_framework import serializers

from web.companies.models import Company
from web.companies.services import DnbServiceClient


class CompanySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = '__all__'

    def get_name(self, instance):
        dnb_company = DnbServiceClient().get_company(
            duns_number=instance.dnb_service_duns_number
        )
        return dnb_company['primary_name']


class SearchCompaniesSerializer(serializers.Serializer):
    search_term = serializers.CharField()
