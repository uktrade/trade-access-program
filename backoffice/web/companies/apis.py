from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from web.companies.models import Company
from web.companies.serializers import (
    SearchCompaniesSerializer, CompanyWriteSerializer, CompanyReadSerializer
)
from web.companies.services import DnbServiceClient, refresh_dnb_company_response_data


class CompaniesViewSet(ModelViewSet):
    queryset = Company.objects.all()
    filterset_fields = ['duns_number', 'name']

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
        client = DnbServiceClient()
        dnb_companies = client.search_companies(search_term=serializer.data['search_term'])
        return Response(dnb_companies)
