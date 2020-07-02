from django.urls import path
from django.views.generic import TemplateView

from api.apply.views import StartApplicationView, EligibilityView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),
    path('eligibility', EligibilityView.as_view()),
    path('start', StartApplicationView.as_view()),
    path('confirmation', TemplateView.as_view(template_name='confirmation.html')),
]
