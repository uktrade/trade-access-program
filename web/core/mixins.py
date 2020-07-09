class FlowFormSubmitMixin:

    def form_valid(self, form):
        instance = form.save(commit=False)

        for field, value in form.cleaned_data.items():
            setattr(instance, field, value)
            setattr(self.request.activation.process, field, value)

        instance.save()

        return super().form_valid(form)
