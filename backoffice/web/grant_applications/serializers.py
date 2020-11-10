from rest_framework import serializers

from web.companies.models import Company, DnbGetCompanyResponse
from web.companies.services import refresh_dnb_company_response_data
from web.grant_applications.models import GrantApplication, StateAid
from web.grant_management.models import GrantManagementProcess
from web.sectors.models import Sector
from web.trade_events.models import Event


class DnbGetCompanyResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = DnbGetCompanyResponse
        fields = ['id', 'dnb_data', 'registration_number', 'company_address']


class CompanySerializer(serializers.ModelSerializer):
    last_dnb_get_company_response = DnbGetCompanyResponseSerializer()
    previous_applications = serializers.SerializerMethodField()
    applications_in_review = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'duns_number', 'registration_number', 'name', 'last_dnb_get_company_response',
            'previous_applications', 'applications_in_review'
        ]
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


class GrantApplicationReadSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    event = EventSerializer()
    sector = SectorSerializer()
    grant_management_process = GrantManagementProcessSerializer()

    class Meta:
        model = GrantApplication
        fields = '__all__'


class GrantApplicationWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = GrantApplication
        fields = '__all__'

    def save(self, **kwargs):
        super(GrantApplicationWriteSerializer, self).save()
        if self.instance.company:
            refresh_dnb_company_response_data(self.instance.company)


class SendForReviewWriteSerializer(serializers.ModelSerializer):
    application_summary = serializers.JSONField()

    class Meta:
        model = GrantApplication
        fields = ['application_summary']


class StateAidSerializer(serializers.ModelSerializer):

    class Meta:
        model = StateAid
        fields = '__all__'
