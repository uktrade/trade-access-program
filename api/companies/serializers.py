from rest_framework.serializers import ModelSerializer

from api.companies.models import Company


class CompanySerializer(ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'
