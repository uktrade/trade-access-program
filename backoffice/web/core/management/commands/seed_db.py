import logging

from django.core.management.base import BaseCommand

from web.companies.models import Company
from web.sectors.models import Sector
from web.tests.factories.grant_applications import CompletedGrantApplicationFactory
from web.trade_events.models import Event


class Command(BaseCommand):
    help = "Seed the database with some fake data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number-of-grant-applications",
            help="Number of NEW grant applications to generate",
            type=int,
            default=5
        )

    def handle(self, *args, **options):
        num = options['number_of_grant_applications']

        company, _ = Company.objects.get_or_create(
            # Uses a real dnb-service duns_number here
            duns_number='239896579', registration_number='03977902', name='GOOGLE UK LIMITED'
        )
        random_event = Event.objects.first()
        random_sector = Sector.objects.first()
        gas = CompletedGrantApplicationFactory.create_batch(
            size=num, company=company, event=random_event, sector=random_sector
        )

        logging.disable(logging.WARNING)
        for ga in gas:
            ga.send_for_review()

        self.stdout.write(self.style.SUCCESS(f"Successfully created {num} NEW grant applications."))
