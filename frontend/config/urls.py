"""tap URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

handler404 = 'web.core.views.handler404'
handler500 = 'web.core.views.handler500'

urlpatterns = [
    # The govuk-frontend stylesheet requires a specific assets location
    # eg. node_modules/govuk-frontend/govuk/helpers/_font-faces.scss
    path(
        'assets/<path:asset_path>',
        RedirectView.as_view(url='/static/govuk-frontend/govuk/assets/%(asset_path)s'),
    ),
    path(
        'hmcts-assets/<path:asset_path>',
        RedirectView.as_view(url='/static/@hmcts/frontend/assets/%(asset_path)s'),
    ),

    # Templates
    path('', RedirectView.as_view(url='grant-applications/')),
    path('users/', include('web.users.urls', namespace='users')),
    path('grant-applications/', include('web.grant_applications.urls', namespace='grant-applications')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url('^__debug__/', include(debug_toolbar.urls)),
        path('admin/', admin.site.urls),
    ] + urlpatterns
