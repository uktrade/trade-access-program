import factory
from django.utils import timezone

from web.trade_events.models import Event


class EventFactory(factory.DjangoModelFactory):
    class Meta:
        model = Event

    name = factory.Sequence(lambda n: f'name-{n}')
    sector = factory.Sequence(lambda n: f'sector-{n}')
    sub_sector = factory.Sequence(lambda n: f'sub_sector-{n}')
    city = factory.Sequence(lambda n: f'city-{n}')
    country = factory.Sequence(lambda n: f'country-{n}')
    start_date = timezone.now().date() + timezone.timedelta(days=1)
    end_date = timezone.now().date() + timezone.timedelta(days=1)
    show_type = 'Physical'
    tcp = factory.Sequence(lambda n: f'tcp-{n}')
    tcp_website = factory.Sequence(lambda n: f'www.website-{n}.com')
