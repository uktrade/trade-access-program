from web.grant_management.services import SupportingInformationContent


class SupportingInformationMixin:

    def get(self, request, *args, **kwargs):
        self.supporting_information = SupportingInformationContent(
            grant_application=self.activation.process.grant_application
        )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'get_supporting_information'):
            context['supporting_information'] = self.get_supporting_information()
        return context
