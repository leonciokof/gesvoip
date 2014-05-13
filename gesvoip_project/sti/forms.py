# -*- coding: utf-8 -*-

from django import forms

from . import models
from gesvoip import choices


class CentrosLocalesForm(forms.ModelForm):

    class Meta:
        model = models.CentrosLocales
        labels = {
            'cod_empresa': u'Codigo Empresa:',
            'cod_centro_local': u'Codigo Local:',
            'desp_centro_local': u'Descripcion Local:',
        }
        widgets = {
            'cod_empresa': forms.TextInput(
                attrs={'required': 'required', 'autofocus': 'autofocus'}),
            'cod_centro_local': forms.TextInput(
                attrs={'required': 'required'}),
            'desp_centro_local': forms.TextInput(
                attrs={'required': 'required'}),
        }


class UpdateCentrosLocalesForm(forms.ModelForm):

    class Meta:
        model = models.CentrosLocales
        exclude = ('cod_centro_local',)
        labels = {
            'cod_empresa': u'Codigo Empresa:',
            'desp_centro_local': u'Descripcion Local:',
        }
        widgets = {
            'cod_empresa': forms.TextInput(
                attrs={'required': 'required', 'autofocus': 'autofocus'}),
            'desp_centro_local': forms.TextInput(
                attrs={'required': 'required'}),
        }


class FechaForm(forms.Form):

    MONTHS = list(choices.MONTHS)
    MONTHS.insert(0, ('', '---------'))
    YEARS = choices.YEARS
    YEARS.insert(0, ('', '---------'))
    month = forms.ChoiceField(
        label='Mes',
        choices=MONTHS,
        widget=forms.Select(attrs={'required': 'required'}))
    year = forms.ChoiceField(
        label='Año',
        choices=YEARS,
        widget=forms.Select(attrs={'required': 'required'}))
