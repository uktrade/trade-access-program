from rest_framework import serializers

from web.companies.models import Company, DnbGetCompanyResponse


class DnbGetCompanyResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = DnbGetCompanyResponse
        fields = '__all__'


class CompanyReadSerializer(serializers.ModelSerializer):
    dnb_get_company_responses = DnbGetCompanyResponseSerializer(many=True)

    class Meta:
        model = Company
        fields = '__all__'


class CompanyWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'


class SearchCompaniesSerializer(serializers.Serializer):
    search_term = serializers.CharField()
