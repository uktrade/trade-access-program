from django.contrib import admin

from web.companies.models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    fields = ['id', 'duns_number', 'created', 'updated']
    readonly_fields = ['id', 'created', 'updated']
    list_display = ['id', 'duns_number', 'created', 'updated']
