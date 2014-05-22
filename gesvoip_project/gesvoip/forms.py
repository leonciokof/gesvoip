# -*- coding: utf-8 -*-

from django import forms

from . import choices, models


class EmailTextInput(forms.widgets.TextInput):

    input_type = 'email'


class NumberTextInput(forms.widgets.TextInput):

    input_type = 'number'


class CdrForm(forms.Form):

    year = forms.ChoiceField(
        label='Seleccionar año',
        choices=choices.YEARS,
        widget=forms.Select(attrs={'required': 'required'}))
    month = forms.ChoiceField(
        label='Seleccionar mes',
        choices=choices.MONTHS,
        widget=forms.Select(attrs={'required': 'required'}))
    incoming_entel = forms.FileField(
        label='ENTEL',
        widget=forms.FileInput(attrs={'required': 'required'}))
    incoming_ctc = forms.FileField(
        label='CTC',
        widget=forms.FileInput(attrs={'required': 'required'}))
    outgoing = forms.FileField(
        label='STI',
        widget=forms.FileInput(attrs={'required': 'required'}))


class RateForm(forms.Form):

    company = forms.ModelChoiceField(
        label='Seleccionar compañia',
        queryset=models.Company.objects.all(),
        widget=forms.Select(attrs={'required': 'required'}))
    year = forms.ChoiceField(
        label='Seleccionar año',
        choices=choices.YEARS,
        widget=forms.Select(attrs={'required': 'required'}))
    month = forms.ChoiceField(
        label='Seleccionar mes',
        choices=choices.MONTHS,
        widget=forms.Select(attrs={'required': 'required'}))
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
