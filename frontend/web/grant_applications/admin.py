from django.contrib import admin

from web.grant_applications.models import GrantApplicationLink


@admin.register(GrantApplicationLink)
class GrantApplicationLinkAdmin(admin.ModelAdmin):
    fields = ['id', 'backoffice_grant_application_id', 'created', 'updated']
    readonly_fields = ['id', 'backoffice_grant_application_id', 'created', 'updated']
    list_display = ['id', 'backoffice_grant_application_id', 'created', 'updated']
