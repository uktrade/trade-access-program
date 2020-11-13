from django.contrib.auth import get_user_model, logout
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from web.users import services
from web.users.forms import SendMagicLinkForm


class MagicLinkView(TemplateView):
    template_name = 'users/magic_link.html'

    def get(self, request, *args, **kwargs):
        form = SendMagicLinkForm()
        return self.render_to_response(
            context={
                'page': {
                    'heading': _('Login'),
                },
                'button_text': _('Send link'),
                'form': form,
            }
        )

    def post(self, request, *args, **kwargs):
        logout(request)
        form = SendMagicLinkForm(data=request.POST)

        if form.is_valid():
            user, created = get_user_model().objects.get_or_create_user(**form.cleaned_data)
            services.send_magic_link(
                user=user,
                login_path=request.build_absolute_uri(reverse('users:magic-link'))  # TODO change to login
            )
            request.session['email'] = user.email
            form.hide_email_field()
            return self.render_to_response(
                context={
                    'page': {
                        'heading': _('Check your email'),
                    },
                    'button_text': _('Resend link'),
                    'magic_link_sent': True,
                    'form': form,
                }
            )

        return self.render_to_response(
            context={
                'page': {
                    'heading': _('Login'),
                },
                'button_text': _('Send link'),
                'form': form
            }
        )
