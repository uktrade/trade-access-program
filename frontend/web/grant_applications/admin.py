from django.contrib import admin

from web.grant_applications.models import GrantApplicationLink


@admin.register(GrantApplicationLink)
class GrantApplicationLinkAdmin(admin.ModelAdmin):
    fields = [
        'id', 'email', 'backoffice_grant_application_id', 'has_viewed_review_page', 'created', 'updated'
    ]
    readonly_fields = [
        'id', 'email', 'admin_state_url_name', 'resume_url', 'backoffice_grant_application_id', 'has_viewed_review_page', 'created', 'updated'
    ]
    list_display = [
        'id', 'email', 'admin_state_url_name', 'resume_url', 'backoffice_grant_application_id', 'has_viewed_review_page', 'created', 'updated'
    ]

    def admin_state_url_name(self, obj):
        return obj.state_url_name or self.model.APPLICATION_FIRST_STEP_URL_NAME
