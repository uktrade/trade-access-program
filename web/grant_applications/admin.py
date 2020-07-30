from django.contrib import admin

from web.grant_applications.models import GrantApplication


@admin.register(GrantApplication)
class GrantApplicationAdmin(admin.ModelAdmin):
    fields = [field.name for field in GrantApplication._meta.get_fields()]
    readonly_fields = ['id', 'created', 'updated']
    list_display = ['id', 'duns_number', 'created', 'updated']
