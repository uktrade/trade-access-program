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
from django.views.generic import TemplateView, RedirectView
from material.frontend import urls as viewflow_frontend_urls

urlpatterns = [
    # The govuk-frontend stylesheet requires a specific assets location
    # eg. node_modules/govuk-frontend/govuk/helpers/_font-faces.scss
    path(
        "assets/<path:asset_path>",
        RedirectView.as_view(url="/static/govuk/assets/%(asset_path)s"),
    ),

    # Viewflow urls includes django '/admin' and '/accounts'
    path('', include(viewflow_frontend_urls)),

    # Templates
    path('', TemplateView.as_view(template_name='core/index.html')),
    path('apply/', include('web.apply.urls', namespace='apply')),

    # API
    path('api/', include('web.companies.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url('^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
