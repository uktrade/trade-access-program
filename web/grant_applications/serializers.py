from rest_framework import serializers

from web.companies.models import Company


class AboutYourBusinessTableSerializer(serializers.ModelSerializer):
    dnb_service_duns_number = serializers.CharField(label='Dun and Bradstreet Number')
    name = serializers.CharField(label='Company Name')
    previous_applications = serializers.SerializerMethodField(label='Previous Applications')

    class Meta:
        model = Company
        fields = ['dnb_service_duns_number', 'name', 'previous_applications']

    def get_previous_applications(self, company):
        return company.grantapplication_set.count()
