from django.contrib.auth.admin import UserAdmin

from web.users.models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'is_active', 'last_login')
    list_filter = ('email', 'is_active',)
    search_fields = ('email',)
    ordering = ('email',)
