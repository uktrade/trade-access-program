from rest_framework.viewsets import ReadOnlyModelViewSet

from api.companies.models import Company
from api.companies.serializers import CompanySerializer


class CompaniesViewSet(ReadOnlyModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filterset_fields = ['registration_number']
