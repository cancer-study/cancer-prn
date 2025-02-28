from django import forms
from django.apps import apps as django_apps
from edc_form_validators import FormValidator, FormValidatorMixin

from ..models import DeathReport


class SubjectDeathFormValidator(FormValidator):

    def clean(self):

        consent_datetime = self.get_consent_datetime()
        death_date = self.cleaned_data.get('death_date', None)
        if (consent_datetime and death_date and
                consent_datetime.date() >= death_date):
            raise forms.ValidationError({
                'death_date':
                f'The death date {death_date}, can not be before enrolment'
                f' date {consent_datetime.date()}'})

        self.m2m_other_specify(
            'Other, specify',
            m2m_field='death_cause_info',
            field_other='death_cause_info_other')

        self.m2m_other_specify(
            'Other, specify',
            m2m_field='death_cause_category',
            field_other='death_cause_other')

    def get_consent_datetime(self):
        subject_identifier = self.cleaned_data.get('subject_identifier')
        consent_model_cls = django_apps.get_model(
            'cancer_subject.subjectconsent')
        try:
            consent_obj = consent_model_cls.objects.filter(
                subject_identifier=subject_identifier).latest('consent_datetime')
        except consent_model_cls.DoesNotExist:
            return None
        else:
            return getattr(
                consent_obj, 'consent_datetime', None)


class SubjectDeathForm(FormValidatorMixin, forms.ModelForm):

    form_validator_cls = SubjectDeathFormValidator

    class Meta:
        model = DeathReport
        fields = '__all__'
