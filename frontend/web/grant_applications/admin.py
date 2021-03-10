from django.contrib import admin

from web.grant_applications.models import GrantApplicationLink


@admin.register(GrantApplicationLink)
class GrantApplicationLinkAdmin(admin.ModelAdmin):
    fields = (
        'id',
        'email',
        'backoffice_grant_application_id',
        'has_viewed_review_page',
        'state_url_name',
        'created',
        'updated'
    )
    readonly_fields = (
        'id',
        'email',
        'backoffice_grant_application_id',
        'has_viewed_review_page',
        'state_url_name',
        'created',
        'updated'
    )
    list_display = (
        'id',
        'email',
        'backoffice_grant_application_id',
        'has_viewed_review_page',
        'created',
        'updated'
    )
