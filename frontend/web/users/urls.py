from django.urls import path

from web.users.views import MagicLinkView

app_name = 'users'

urlpatterns = [
    path('magic-link/', MagicLinkView.as_view(), name='magic-link'),
    # path('login/', LoginView.as_view(), name='login')
]
