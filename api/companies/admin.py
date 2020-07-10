from django.contrib import admin

from api.companies.models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    fields = ['id', 'dnb_service_duns_number', 'created', 'updated']
    readonly_fields = ['id', 'created', 'updated']
    list_display = ['id', 'dnb_service_duns_number', 'created', 'updated']
