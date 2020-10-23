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
    search_term = serializers.CharField(min_length=2, max_length=60, required=False)
    primary_name = serializers.CharField(min_length=2, max_length=60, required=False)
    registration_numbers = serializers.ListField(
        child=serializers.CharField(min_length=1, max_length=60), min_length=1, required=False
    )
    duns_number = serializers.CharField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not any(field in attrs for field in self.fields):
            raise serializers.ValidationError(f"One of: {', '.join(self.fields)} is required.")
        return attrs
