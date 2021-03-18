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
from django.urls import path, include
from django.views.generic import RedirectView
from material.frontend.urls import modules as viewflow_apps

from web.core.views import IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),

    # The govuk-frontend stylesheet requires a specific assets location
    # eg. node_modules/govuk-frontend/govuk/helpers/_font-faces.scss
    path(
        "assets/<path:asset_path>",
        RedirectView.as_view(url='/static/govuk/assets/%(asset_path)s'),
    ),
    path('auth/', include('authbroker_client.urls')),

    # Viewflow urls (includes the django /admin site)
    path('', include(viewflow_apps.urls)),

    # API
    path('api/', include('web.companies.api_urls')),
    path('api/', include('web.grant_applications.api_urls')),
    path('api/', include('web.sectors.api_urls')),
    path('api/', include('web.trade_events.api_urls')),
]

if settings.DEBUG:
    import debug_toolbar
    from django.views.static import serve
    urlpatterns = [
        url('^__debug__/', include(debug_toolbar.urls)),
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ] + urlpatterns
