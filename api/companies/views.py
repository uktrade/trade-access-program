from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api.companies.models import Company
from api.companies.serializers import CompanySerializer, SearchCompaniesSerializer
from api.companies.services import DnbServiceClient


class CompaniesViewSet(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class SearchCompaniesView(APIView):

    def get(self, request, *args, **kwargs):
        serializer = SearchCompaniesSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        client = DnbServiceClient()
        dnb_companies = client.search_companies(search_term=serializer.data['search_term'])
        return Response(dnb_companies)
