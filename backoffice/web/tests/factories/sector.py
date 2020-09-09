import factory

from web.sectors.models import Sector


class SectorFactory(factory.DjangoModelFactory):
    class Meta:
        model = Sector

    sector_code = factory.Sequence(lambda n: f'SL{n:04}')
    name = factory.Sequence(lambda n: f'name-{n}')
    cluster_name = factory.Sequence(lambda n: f'cluster-name-{n}')
    full_name = factory.Sequence(lambda n: f'full-name-{n}')
    sub_sector_name = factory.Sequence(lambda n: f'sub-sector-name-{n}')
    sub_sub_sector_name = factory.Sequence(lambda n: f'sub-sub-sector-name-{n}')
