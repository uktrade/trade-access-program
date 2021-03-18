from django.contrib import admin

from web.core.models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'uploaded_at')
    list_filter = ('uploaded_at',)
