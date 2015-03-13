# -*- coding: utf-8 -*-

from django import forms

from crispy_forms.helper import FormHelper
from mongodbforms import DocumentForm

from . import choices, models


class EmailTextInput(forms.widgets.TextInput):

    input_type = 'email'


class NumberTextInput(forms.widgets.TextInput):

    input_type = 'number'


class CdrForm(DocumentForm):

    class Meta:
        document = models.Cdr
        fields = (
            'year', 'month', 'incoming_ctc', 'incoming_entel', 'outgoing')

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.html5_required = True
        super(CdrForm, self).__init__(*args, **kwargs)


class RateForm(forms.Form):

    company = forms.ModelChoiceField(
        label='Seleccionar compañia',
        queryset=models.Company.objects.all(),
        widget=forms.Select(
            attrs={'required': 'required', 'class': 'select2'}))
    start = forms.CharField(
        label='Fecha inicio',
        widget=forms.TextInput(
            attrs={'class': 'datepicker', 'data-date-format': 'YYYY-MM-DD'}))
    end = forms.CharField(
        label='Fecha fin',
        widget=forms.TextInput(
            attrs={'class': 'datepicker', 'data-date-format': 'YYYY-MM-DD'}))
    normal_price = forms.FloatField(
        label='Valor horario normal ($/seg)',
        widget=NumberTextInput(attrs={
            'required': 'required',
            'min': '0.0001',
            'step': '0.0001',
            'placeholder': '0.0001'}))
    reduced_price = forms.FloatField(
        label='Valor horario reducido ($/seg)',
        widget=NumberTextInput(attrs={
            'required': 'required',
            'min': '0.0001',
            'step': '0.0001',
            'placeholder': '0.0001'}))
    nightly_price = forms.FloatField(
        label='Valor horario ncturno ($/seg)',
        widget=NumberTextInput(attrs={
            'required': 'required',
            'min': '0.0001',
            'step': '0.0001',
            'placeholder': '0.0001'}))


class CompanyForm(DocumentForm):
    bussines_normal_start = forms.CharField(
        label='Horario habil normal inicio',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    bussines_normal_end = forms.CharField(
        label='Horario habil normal fin',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    bussines_reduced_start = forms.CharField(
        label='Horario habil reducido inicio',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    bussines_reduced_end = forms.CharField(
        label='Horario habil reducido fin',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    bussines_nightly_start = forms.CharField(
        label='Horario habil nocturno inicio',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    bussines_nightly_end = forms.CharField(
        label='Horario habil nocturno fin',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    saturday_normal_start = forms.CharField(
        label='Horario sabado normal inicio',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    saturday_normal_end = forms.CharField(
        label='Horario sabado normal fin',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    saturday_reduced_start = forms.CharField(
        label='Horario sabado reducido inicio',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    saturday_reduced_end = forms.CharField(
        label='Horario sabado reducido fin',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    saturday_nightly_start = forms.CharField(
        label='Horario sabado nocturno inicio',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    saturday_nightly_end = forms.CharField(
        label='Horario sabado nocturno fin',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    festive_normal_start = forms.CharField(
        label='Horario festivo normal inicio',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    festive_normal_end = forms.CharField(
        label='Horario festivo normal fin',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    festive_reduced_start = forms.CharField(
        label='Horario festivo reducido inicio',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    festive_reduced_end = forms.CharField(
        label='Horario festivo reducido fin',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    festive_nightly_start = forms.CharField(
        label='Horario festivo nocturno inicio',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))
    festive_nightly_end = forms.CharField(
        label='Horario festivo nocturno fin',
        required=False,
        widget=forms.TextInput(attrs={'class': 'timepicker'}))

    class Meta:
        document = models.Company
        exclude = ('schedules',)


class HolidayForm(DocumentForm):
    date = forms.CharField(
        label='Fecha',
        widget=forms.TextInput(
            attrs={'class': 'datepicker', 'data-date-format': 'YYYY-MM-DD'}))

    class Meta:
        document = models.Holiday


class LineForm(DocumentForm):

    class Meta:
        document = models.Line
        widgets = {
            'zone': forms.Select(attrs={'class': 'select2'}),
            'city': forms.Select(attrs={'class': 'select2'}),
        }


class LineRangeForm(DocumentForm):
    start = forms.IntegerField(
        label='Inicio',
        widget=NumberTextInput())
    end = forms.IntegerField(
        label='Fin',
        widget=NumberTextInput())

    class Meta:
        document = models.Line
        exclude = ('number',)
        widgets = {
            'zone': forms.Select(attrs={'class': 'select2'}),
            'city': forms.Select(attrs={'class': 'select2'}),
        }

    def __init__(self, *args, **kwargs):
        super(LineRangeForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'start',
            'end',
            'rut',
            'service',
            'mode',
            'due',
            'active',
            'document',
            'special_service',
            'name',
            'entity',
            'comments',
            'zone',
            'city',
        ]


class ReportForm(forms.Form):

    year = forms.ChoiceField(
        label='Seleccionar año',
        choices=choices.YEARS,
        widget=forms.Select(attrs={'required': 'required'}))
    month = forms.ChoiceField(
        label='Seleccionar mes',
        choices=choices.MONTHS,
        widget=forms.Select(attrs={'required': 'required'}))


class CcaaForm(DocumentForm):
    start = forms.CharField(
        label='Fecha inicio',
        widget=forms.TextInput(
            attrs={'class': 'datepicker', 'data-date-format': 'YYYY-MM-DD'}))
    end = forms.CharField(
        label='Fecha fin',
        widget=forms.TextInput(
            attrs={'class': 'datepicker', 'data-date-format': 'YYYY-MM-DD'}))
    invoice_date = forms.CharField(
        label='Fecha emision factura',
        widget=forms.TextInput(
            attrs={'class': 'datepicker', 'data-date-format': 'YYYY-MM-DD'}))

    class Meta:
        document = models.Ccaa
        widgets = {
            'company': forms.Select(attrs={'class': 'select2'}),
        }


class PortabilityUploadForm(forms.Form):

    file_portability = forms.FileField(label='Archivo (CSV)')


class NumerationUploadForm(forms.Form):

    file_numeration = forms.FileField(label='Archivo (CSV)')
