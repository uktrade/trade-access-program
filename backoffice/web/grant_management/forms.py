from django import forms
from material import Layout, Row, Column, Span4

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
        widget=forms.RadioSelect(
            choices=GrantManagementProcess.VerifyChoices.choices
        )
    )


class VerifyBusinessEntityForm(forms.ModelForm):
    class Meta:
        model = GrantManagementProcess
        fields = ['business_entity_is_verified']

    business_entity_is_verified = forms.BooleanField(
        widget=forms.RadioSelect(
            choices=GrantManagementProcess.VerifyChoices.choices
        )
    )


class VerifyStateAidForm(forms.ModelForm):
    class Meta:
        model = GrantManagementProcess
        fields = ['state_aid_is_verified']

    state_aid_is_verified = forms.BooleanField(
        widget=forms.RadioSelect(
            choices=GrantManagementProcess.VerifyChoices.choices
        )
    )


class ProductsAndServicesForm(forms.ModelForm):
    layout = Layout(
        Row('products_and_services_score'),
        Row(Span4('products_and_services_justification'), Column())
    )

    class Meta:
        model = GrantManagementProcess
        fields = ['products_and_services_score', 'products_and_services_justification']

    products_and_services_score = forms.IntegerField(
        label='Score',
        widget=forms.RadioSelect(choices=GrantManagementProcess.ScoreChoices.choices)
    )
    products_and_services_justification = forms.CharField(
        label='Justification'
    )


class ExportStrategyForm(forms.ModelForm):
    layout = Layout(
        Row('export_strategy_score'),
        Row(Span4('export_strategy_justification'), Column())
    )

    class Meta:
        model = GrantManagementProcess
        fields = ['export_strategy_score', 'export_strategy_justification']

    export_strategy_score = forms.IntegerField(
        label='Score',
        widget=forms.RadioSelect(choices=GrantManagementProcess.ScoreChoices.choices)
    )
    export_strategy_justification = forms.CharField(
        label='Justification'
    )
