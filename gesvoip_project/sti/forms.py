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


class DatoForm(forms.Form):

    dato = forms.CharField(
        label='Consulta por Numero, Rut:',
        widget=forms.TextInput(
            attrs={
                'required': 'required', 'autofocus': 'autofocus',
                'class': 'text'}))


class PnMtcForm(forms.ModelForm):

    class Meta:
        model = models.PnMtc
        fields = (
            'numero_telefono',
            'rut_propietario',
            'tipo_servicio',
            'modalidad',
            'deuda_vencida',
            'tipo_servicio_especial',
            'estado',
        )
        labels = {
            'rut_propietario': u'Rut',
            'tipo_servicio': u'Tipo Servicio',
            'modalidad': u'Modalidad',
            'deuda_vencida': u'Deuda',
            'tipo_servicio_especial': u'Servicio Especial',
            'estado': u'Estado',
        }
        widgets = {
            'numero_telefono': forms.HiddenInput(),
            'rut_propietario': forms.TextInput(
                attrs={
                    'required': 'required', 'autofocus': 'autofocus'}),
            'tipo_servicio': forms.Select(
                attrs={'required': 'required'}),
            'modalidad': forms.Select(
                attrs={'required': 'required'}),
            'deuda_vencida': forms.TextInput(
                attrs={'required': 'required'}),
            'tipo_servicio_especial': forms.Select(
                attrs={'required': 'required'}),
            'estado': forms.Select(
                attrs={'required': 'required'}),
        }


class LineasForm(forms.ModelForm):

    class Meta:
        model = models.Lineas
        fields = (
            'numero',
            'nombre',
            'tipo_persona',
            'area',
            'comuna',
            'comentarios',
        )
        widgets = {
            'numero': forms.HiddenInput(),
            'nombre': forms.TextInput(
                attrs={'required': 'required', 'autofocus': 'autofocus'}),
            'tipo_persona': forms.Select(
                attrs={'required': 'required'}),
            'area': forms.Select(
                attrs={'required': 'required'}),
            'comuna': forms.Select(
                attrs={'required': 'required'}),
            'comentarios': forms.Textarea(
                attrs={'required': 'required', 'class': 'text'}),
        }
