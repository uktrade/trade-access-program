from django import forms
from django.conf import settings
from material import Layout, Row, Column, Span4

from web.grant_management.models import GrantManagementProcess

VERIFY_CHOICES = ((True, 'Accept'), (False, 'Reject'))
VERIFY_LABEL = 'Do you accept or reject the applicant’s answer?'
SCORE_LABEL = 'How would you assess the applicant’s response?'
RATIONALE_LABEL = 'Rationale'
RATIONALE_PLACEHOLDER = 'Enter your rationale here'


def str_to_bool(value):
    if str(value).lower() in ['true', 't', '1']:
        return True
    elif str(value).lower() in ['false', 'f', '0']:
        return False
    raise ValueError(f'Cannot convert {value} to boolean')


class VerifyPreviousApplicationsForm(forms.ModelForm):
    class Meta:
        model = GrantManagementProcess
        fields = ['previous_applications_is_verified']

    previous_applications_is_verified = forms.TypedChoiceField(
        label=VERIFY_LABEL,
        coerce=str_to_bool,
        choices=VERIFY_CHOICES,
        widget=forms.RadioSelect
    )


class VerifyEventCommitmentForm(forms.ModelForm):
    class Meta:
        model = GrantManagementProcess
        fields = ['event_commitment_is_verified']

    event_commitment_is_verified = forms.TypedChoiceField(
        label=VERIFY_LABEL,
        coerce=str_to_bool,
        choices=VERIFY_CHOICES,
        widget=forms.RadioSelect
    )


class VerifyBusinessEntityForm(forms.ModelForm):
    class Meta:
        model = GrantManagementProcess
        fields = ['business_entity_is_verified']

    business_entity_is_verified = forms.TypedChoiceField(
        label=VERIFY_LABEL,
        coerce=str_to_bool,
        choices=VERIFY_CHOICES,
        widget=forms.RadioSelect
    )


class VerifyStateAidForm(forms.ModelForm):
    class Meta:
        model = GrantManagementProcess
        fields = ['state_aid_is_verified']

    state_aid_is_verified = forms.TypedChoiceField(
        label=VERIFY_LABEL,
        coerce=str_to_bool,
        choices=VERIFY_CHOICES,
        widget=forms.RadioSelect
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
        label=SCORE_LABEL,
        widget=forms.RadioSelect(choices=GrantManagementProcess.ScoreChoices.choices)
    )
    products_and_services_justification = forms.CharField(
        label=RATIONALE_LABEL,
        widget=forms.Textarea(
            attrs={'placeholder': RATIONALE_PLACEHOLDER}
        )
    )


class ProductsAndServicesCompetitorsForm(forms.ModelForm):
    layout = Layout(
        Row('products_and_services_competitors_score'),
        Row(Span4('products_and_services_competitors_justification'), Column())
    )

    class Meta:
        model = GrantManagementProcess
        fields = [
            'products_and_services_competitors_score',
            'products_and_services_competitors_justification'
        ]

    products_and_services_competitors_score = forms.IntegerField(
        label='Score',
        widget=forms.RadioSelect(choices=GrantManagementProcess.ScoreChoices.choices)
    )
    products_and_services_competitors_justification = forms.CharField(
        label=RATIONALE_LABEL,
        widget=forms.Textarea(
            attrs={'placeholder': RATIONALE_PLACEHOLDER}
        )
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
        label=RATIONALE_LABEL,
        widget=forms.Textarea(
            attrs={'placeholder': RATIONALE_PLACEHOLDER}
        )
    )


class EventIsAppropriateForm(forms.ModelForm):
    class Meta:
        model = GrantManagementProcess
        fields = ['event_is_appropriate']

    event_is_appropriate = forms.TypedChoiceField(
        label='Is the trade show appropriate?',
        widget=forms.RadioSelect,
        coerce=str_to_bool,
        choices=settings.BOOLEAN_CHOICES
    )


class DecisionForm(forms.ModelForm):
    class Meta:
        model = GrantManagementProcess
        fields = ['decision']

    decision = forms.CharField(
        widget=forms.RadioSelect(choices=GrantManagementProcess.Decision.choices)
    )
