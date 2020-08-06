class SupportingInformationMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'get_supporting_information_card'):
            context['supporting_information_card'] = self.get_supporting_information_card()
        return context
