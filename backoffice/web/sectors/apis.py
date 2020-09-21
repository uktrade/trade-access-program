from rest_framework.viewsets import ReadOnlyModelViewSet

from web.sectors.models import Sector
from web.sectors.serializers import SectorSerializer


class SectorsViewSet(ReadOnlyModelViewSet):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
