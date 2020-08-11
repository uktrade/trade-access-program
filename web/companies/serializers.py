from rest_framework import serializers

from web.companies.models import Company


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'


class SearchCompaniesSerializer(serializers.Serializer):
    search_term = serializers.CharField()
