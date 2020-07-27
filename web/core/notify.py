import logging

from django.conf import settings
from notifications_python_client import NotificationsAPIClient


class NotifyService:

    def __init__(self, api_client=None):
        self._templates = None
        self.api_client = api_client or NotificationsAPIClient(api_key=settings.NOTIFY_API_KEY)

    @property
    def templates(self):
        if not self._templates:
            templates_list = self.api_client.get_all_templates()['templates']
            self._templates = {t['name']: t for t in templates_list}
        return self._templates

    def _preview_and_log(self, template_id, personalisation):
        preview = self.api_client.post_template_preview(
            template_id=template_id,
            personalisation=personalisation
        )
        logging.info(
            f"Sent {preview['type']}\ntemplate_id: {preview['id']}\n"
            f"subject: {preview['subject']}\nbody: {preview['body']}"
        )
        return preview

    def send_email(self, email_address, template_name, personalisation):
        template_id = self.templates.get(template_name, {}).get('id')

        if settings.NOTIFY_ENABLED:
            return self.api_client.send_email_notification(
                email_address=email_address,
                template_id=template_id,
                personalisation=personalisation
            )

        return self._preview_and_log(
            template_id=template_id,
            personalisation=personalisation
        )

    def send_application_submitted_email(self, email_address, applicant_full_name):
        self.send_email(
            email_address=email_address,
            template_name='application-submitted',
            personalisation={'applicant_full_name': applicant_full_name}
        )
