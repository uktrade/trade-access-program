from rest_framework import serializers

from web.companies.models import Company
from web.grant_management.models import GrantManagementProcess


class AboutYourBusinessTableSerializer(serializers.ModelSerializer):
    duns_number = serializers.CharField(label='Dun and Bradstreet Number')
    name = serializers.CharField(label='Company Name')
    previous_applications = serializers.SerializerMethodField(label='Previous Applications')

    class Meta:
        model = Company
        fields = ['duns_number', 'name', 'previous_applications']

    def get_previous_applications(self, company):
        return company.grantapplication_set.filter(
            grant_application_process__isnull=False,
            grant_application_process__decision=GrantManagementProcess.Decision.APPROVED
        ).count()
