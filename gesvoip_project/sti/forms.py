# -*- coding: utf-8 -*-

from django import forms

from . import choices, models
from gesvoip.choices import MONTHS, YEARS
from gesvoip.forms import NumberTextInput
from gesvoip.models import Compania


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

    MONTHS = list(MONTHS)
    MONTHS.insert(0, ('', '---------'))
    YEARS = list(YEARS)
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


class PortadoForm(forms.Form):

    numero = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                'required': 'required', 'autofocus': 'autofocus',
                'class': 'text', 'placeholder': '56XXXXXXXX'}))


class RangoPortadoForm(forms.Form):

    TIPO_SERVICIOS = list(choices.TIPO_SERVICIOS)
    TIPO_SERVICIOS.insert(0, ('', '---------'))
    MODALIDADES = list(choices.MODALIDADES)
    MODALIDADES.insert(0, ('', '---------'))
    TIPO_SERVICIO_ESPECIALES = list(choices.TIPO_SERVICIO_ESPECIALES)
    TIPO_SERVICIO_ESPECIALES.insert(0, ('', '---------'))
    ESTADOS = list(choices.ESTADOS)
    ESTADOS.insert(0, ('', '---------'))
    TIPO_PERSONAS = list(choices.TIPO_PERSONAS)
    TIPO_PERSONAS.insert(0, ('', '---------'))
    PRIMARIAS = list(choices.PRIMARIAS)
    PRIMARIAS.insert(0, ('', '---------'))
    COMUNAS = list(choices.COMUNAS)
    COMUNAS.insert(0, ('', '---------'))
    rango_inicio = forms.IntegerField(
        widget=NumberTextInput(
            attrs={
                'required': 'required', 'autofocus': 'autofocus',
                'placeholder': '56XXXXXXXX'}))
    rango_fin = forms.IntegerField(
        widget=NumberTextInput(
            attrs={
                'required': 'required', 'placeholder': '56XXXXXXXX'}))
    rut = forms.CharField()
    tipo_servicio = forms.ChoiceField(
        choices=TIPO_SERVICIOS,
        widget=forms.Select(attrs={'required': 'required'}))
    modalidad = forms.ChoiceField(
        choices=MODALIDADES,
        widget=forms.Select(attrs={'required': 'required'}))
    deuda = forms.FloatField(widget=NumberTextInput(), required=False)
    documento = forms.CharField(required=False)
    especial = forms.ChoiceField(
        choices=TIPO_SERVICIO_ESPECIALES,
        widget=forms.Select(attrs={'required': 'required'}))
    estado = forms.ChoiceField(
        choices=ESTADOS,
        widget=forms.Select(attrs={'required': 'required'}))
    nombre_cliente = forms.CharField()
    tipo_persona = forms.ChoiceField(
        choices=TIPO_PERSONAS,
        widget=forms.Select(attrs={'required': 'required'}))
    zona_primaria = forms.ChoiceField(
        choices=PRIMARIAS,
        widget=forms.Select(attrs={'required': 'required'}))
    comuna = forms.ChoiceField(
        choices=COMUNAS,
        widget=forms.Select(attrs={'required': 'required'}))
    comentarios = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'text'}), required=False)


class CcaaForm(forms.ModelForm):

    MONTHS = list(MONTHS)
    MONTHS.insert(0, ('', '---------'))
    YEARS = list(YEARS)
    YEARS.insert(0, ('', '---------'))
    month = forms.ChoiceField(
        label='Mes',
        choices=MONTHS,
        widget=forms.Select(attrs={'required': 'required'}))
    year = forms.ChoiceField(
        label='Año',
        choices=YEARS,
        widget=forms.Select(
            attrs={'required': 'required', 'autofocus': 'autofocus'}))
    concecionaria = forms.ModelChoiceField(
        label='Concecionaria Interconectada',
        queryset=Compania.objects.all(),
        widget=forms.Select(attrs={'required': 'required'}))

    class Meta:
        model = models.Ccaa
        fields = (
            'n_factura',
            'fecha_inicio',
            'fecha_fin',
            'fecha_fact',
            'horario',
            'trafico',
            'monto',
        )
        labels = {
            'n_factura': 'Numero Factura',
            'fecha_fact': 'Fecha Emision Factura',
            'horario': 'Tipo Horario',
        }
        widgets = {
            'n_factura': NumberTextInput(
                attrs={'required': 'required'}),
            'fecha_inicio': forms.TextInput(
                attrs={'required': 'required', 'class': 'datepicker'}),
            'fecha_fin': forms.TextInput(
                attrs={'required': 'required', 'class': 'datepicker'}),
            'fecha_fact': forms.TextInput(
                attrs={'required': 'required', 'class': 'datepicker'}),
            'horario': forms.Select(
                attrs={'required': 'required'}),
            'trafico': NumberTextInput(
                attrs={'required': 'required'}),
            'monto': NumberTextInput(
                attrs={'required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        super(CcaaForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'year',
            'month',
            'concecionaria',
            'n_factura',
            'fecha_inicio',
            'fecha_fin',
            'fecha_fact',
            'horario',
            'trafico',
            'monto']
