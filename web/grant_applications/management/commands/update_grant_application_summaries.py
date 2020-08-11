from django.core.management.base import BaseCommand

from web.grant_applications.models import GrantApplication
from web.grant_applications.views import ApplicationReviewView


class Command(BaseCommand):
    help = "Update all grant application summaries"

    def handle(self, *args, **options):
        gas = GrantApplication.objects.all()

        for ga in gas:
            application_summary = ApplicationReviewView(object=ga).generate_application_summary(ga)
            ga.application_summary = application_summary
            ga.save()

        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated all {len(gas)} grant applications.')
        )
