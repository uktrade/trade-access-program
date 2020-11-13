from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django import forms
from sesame import utils as sesame_utils

from web.core.notify import NotifyService


class SendMagicLinkForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label=_('Enter your email'),
        help_text=_("We'll send you a link to login"),
        widget=forms.TextInput(
            attrs={
                'class': 'govuk-input',
                'autofocus': True,
                'optional_label_override': True,
            }
        )
    )

    def hide_email_field(self):
        self.fields['email'].widget = forms.HiddenInput()

    # def clean(self):
    #     email = self.cleaned_data.get('email')
    #
    #     if email:
    #         user = get_user(request)
    #         self.user_cache = authenticate(self.request, username=username, password=password)
    #         if user is None:
    #             raise forms.ValidationError(
    #                 AuthenticationForm.error_messages['invalid_login'],
    #                 code='invalid_login',
    #                 params={'username': self.username_field.verbose_name},
    #             )
    #         else:
    #             self.confirm_login_allowed(self.user_cache)
    #
    #     return self.cleaned_data
    #
    # def confirm_login_allowed(self, user):
    #     """
    #     Controls whether the given User may log in. This is a policy setting,
    #     independent of end-user authentication. This default behavior is to
    #     allow login by active users, and reject login by inactive users.
    #
    #     If the given user cannot log in, this method should raise a
    #     ``ValidationError``.
    #
    #     If the given user may log in, this method should return None.
    #     """
    #     if not user.is_active:
    #         raise forms.ValidationError(
    #             AuthenticationForm.error_messages['inactive'],
    #             code='inactive',
    #         )
