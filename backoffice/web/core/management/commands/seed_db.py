import logging

from django.core.management.base import BaseCommand

from web.companies.models import Company
from web.grant_applications.views import ApplicationReviewView
from web.tests.factories.grant_applications import GrantApplicationFactory


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

        # Uses a real dnb-service duns_number here
        company, _ = Company.objects.get_or_create(
            duns_number=239896579, name='GOOGLE UK LIMITED'
        )

        gas = GrantApplicationFactory.create_batch(size=num, company=company)

        logging.disable(logging.WARNING)
        for ga in gas:
            application_summary = ApplicationReviewView(object=ga).generate_application_summary(ga)
            ga.application_summary = application_summary
            ga.save()
            ga.send_for_review()

        self.stdout.write(self.style.SUCCESS(f"Successfully created {num} NEW grant applications."))
