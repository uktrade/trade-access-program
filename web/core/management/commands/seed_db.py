import logging

from django.core.management.base import BaseCommand

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
        gas = GrantApplicationFactory.create_batch(size=num)

        logging.disable(logging.WARNING)
        for ga in gas:
            application_summary = ApplicationReviewView(object=ga).generate_application_summary(ga)
            ga.application_summary = application_summary
            ga.save()
            ga.send_for_review()

        self.stdout.write(self.style.SUCCESS(f"Successfully created {num} NEW grant applications."))
