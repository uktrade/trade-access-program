from rest_framework import serializers

from web.companies.models import Company, DnbGetCompanyResponse


class DnbGetCompanyResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = DnbGetCompanyResponse
        fields = ['id', 'company', 'dnb_data', 'registration_number', 'company_address']


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
    search_term = serializers.CharField(required=False)
    duns_number = serializers.CharField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if 'search_term' not in attrs and 'duns_number' not in attrs:
            raise serializers.ValidationError('One of search_term or duns_number required.')
        return attrs
