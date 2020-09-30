from django.contrib import admin

from web.companies.models import Company, DnbGetCompanyResponse


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    fields = ['id', 'name', 'duns_number', 'created', 'updated']
    readonly_fields = ['id', 'name', 'duns_number', 'created', 'updated']
    list_display = ['id', 'name', 'duns_number', 'created', 'updated']


@admin.register(DnbGetCompanyResponse)
class DnbGetCompanyResponseAdmin(admin.ModelAdmin):
    fields = ['id', 'company', 'data', 'created', 'updated']
    readonly_fields = ['id', 'company', 'data', 'created', 'updated']
    list_display = ['id', 'company', 'data', 'created', 'updated']
