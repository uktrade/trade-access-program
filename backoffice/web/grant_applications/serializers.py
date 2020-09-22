from rest_framework import serializers

from web.companies.models import Company
from web.grant_applications.models import GrantApplication
from web.grant_management.models import GrantManagementProcess
from web.sectors.models import Sector
from web.trade_events.models import Event


class CompanySerializer(serializers.ModelSerializer):
    previous_applications = serializers.SerializerMethodField()
    applications_in_review = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'duns_number', 'name', 'previous_applications', 'applications_in_review']
        extra_kwargs = {
            'duns_number': {
                'validators': [],
            }
        }

    def get_applications_in_review(self, company):
        return company.grantapplication_set.filter(
            grant_management_process__isnull=False,
            grant_management_process__decision__isnull=True
        ).count()

    def get_previous_applications(self, company):
        return company.grantapplication_set.filter(
            grant_management_process__isnull=False,
            grant_management_process__decision=GrantManagementProcess.Decision.APPROVED
        ).count()


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = [
            'id', 'name', 'city', 'country', 'show_type', 'start_date', 'end_date', 'sector',
            'sub_sector', 'tcp', 'tcp_website'
        ]


class SectorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sector
        fields = ['id', 'full_name']


class GrantManagementProcessSerializer(serializers.ModelSerializer):

    class Meta:
        model = GrantManagementProcess
        fields = [
            'id', 'status', 'finished', 'employee_count_is_verified', 'turnover_is_verified',
            'decision', 'artifact_content_type', 'grant_application'
        ]


class GrantApplicationCompanySerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    event = EventSerializer()
    sector = SectorSerializer()
    grant_management_process = GrantManagementProcessSerializer()

    class Meta:
        model = GrantApplication
        fields = '__all__'


class GrantApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = GrantApplication
        fields = '__all__'
