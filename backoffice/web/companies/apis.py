from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from web.companies.models import Company, DnbGetCompanyResponse
from web.companies.serializers import (
    SearchCompaniesSerializer, CompanyWriteSerializer, CompanyReadSerializer,
    DnbGetCompanyResponseSerializer
)

from web.companies.services import refresh_dnb_company_response_data, DnbServiceClient


class CompaniesViewSet(ModelViewSet):
    queryset = Company.objects.all()
    filterset_fields = ['duns_number', 'registration_number', 'name']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CompanyWriteSerializer
        return CompanyReadSerializer

    def perform_create(self, serializer):
        company = serializer.save()
        refresh_dnb_company_response_data(company)


class SearchCompaniesView(APIView):

    def get(self, request, *args, **kwargs):
        serializer = SearchCompaniesSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        dnb_client = DnbServiceClient()
        companies_data = dnb_client.search_companies(**serializer.validated_data)
        companies = DnbGetCompanyResponseSerializer(
            instance=[DnbGetCompanyResponse(dnb_data=d) for d in companies_data],
            many=True
        )
        return Response(companies.data)
