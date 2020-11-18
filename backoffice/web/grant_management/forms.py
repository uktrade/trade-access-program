from django import forms

from web.grant_management.models import GrantManagementProcess


class VerifyPreviousApplicationsForm(forms.ModelForm):

    class Meta:
        model = GrantManagementProcess
        fields = ['previous_applications_is_verified']

    previous_applications_is_verified = forms.BooleanField(
        required=True,
        widget=forms.RadioSelect(
            choices=GrantManagementProcess.VerifyChoices.choices
        )
    )


class VerifyEventCommitmentForm(forms.ModelForm):
    class Meta:
        model = GrantManagementProcess
        fields = ['event_commitment_is_verified']

    event_commitment_is_verified = forms.BooleanField(
        required=True,
        widget=forms.RadioSelect(
            choices=GrantManagementProcess.VerifyChoices.choices
        )
    )


class VerifyBusinessEntityForm(forms.ModelForm):
    class Meta:
        model = GrantManagementProcess
        fields = ['business_entity_is_verified']

    business_entity_is_verified = forms.BooleanField(
        required=True,
        widget=forms.RadioSelect(
            choices=GrantManagementProcess.VerifyChoices.choices
        )
    )


class VerifyStateAidForm(forms.ModelForm):
    class Meta:
        model = GrantManagementProcess
        fields = ['state_aid_is_verified']

    state_aid_is_verified = forms.BooleanField(
        required=True,
        widget=forms.RadioSelect(
            choices=GrantManagementProcess.VerifyChoices.choices
        )
    )
