# -*- coding: utf-8 -*-

from django import forms

from . import models


class EmailTextInput(forms.widgets.TextInput):

    input_type = 'email'


class UsuariosForm(forms.ModelForm):

    class Meta:
        model = models.Usuarios
        exclude = ('id_usuario',)
        labels = {'password': u'Contraseña'}
        widgets = {
            'usuario': forms.TextInput(attrs={'required': 'required'}),
            'password': forms.PasswordInput(attrs={'required': 'required'}),
            'nombre': forms.TextInput(attrs={'required': 'required'}),
            'apellido': forms.TextInput(attrs={'required': 'required'}),
            'correo': EmailTextInput(attrs={'required': 'required'}),
            'rol': forms.Select(attrs={'required': 'required'}),
        }


class BuscaUserForm(forms.Form):

    usuario = forms.ModelChoiceField(
        label='Seleccionar usuario',
        queryset=models.Usuarios.objects.all(),
        widget=forms.Select(attrs={'required': 'required'}))


class CompaniaForm(forms.ModelForm):

    horario_habil_normal_inicio = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_habil_normal_fin = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_habil_reducido_inicio = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_habil_reducido_fin = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_habil_nocturno_inicio = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_habil_nocturno_fin = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_reducido_normal_inicio = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_reducido_normal_fin = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_reducido_reducido_inicio = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_reducido_reducido_fin = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_reducido_nocturno_inicio = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_reducido_nocturno_fin = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_nocturno_normal_inicio = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_nocturno_normal_fin = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_nocturno_reducido_inicio = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_nocturno_reducido_fin = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_nocturno_nocturno_inicio = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))
    horario_nocturno_nocturno_fin = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'time'}))

    class Meta:
        model = models.Compania
        exclude = ('id_compania', 'entidad')
        widgets = {
            'nombre': forms.TextInput(
                attrs={'required': 'required', 'class': 'text'}),
            'rut': forms.TextInput(
                attrs={
                    'required': 'required', 'class': 'text',
                    'placeholder': 'Ingresar RUT sin puntos ni guion'}),
            'id': forms.TextInput(
                attrs={'required': 'required', 'class': 'text'}),
            'codigo': forms.TextInput(
                attrs={'required': 'required', 'class': 'text'}),
        }


class BuscaCompaniaForm(forms.Form):

    compania = forms.ModelChoiceField(
        label='Seleccionar compañia',
        queryset=models.Compania.objects.all(),
        widget=forms.Select(attrs={'required': 'required'}))


class CdrForm(forms.ModelForm):

    class Meta:
        model = models.Cdr
        exclude = ('fecha', 'processed')
        labels = {
            'month': u'Mes', 'year': u'Año', 'compania': u'Compañia',
            'source': 'Archivo',
        }
        widgets = {
            'compania': forms.Select(attrs={'required': 'required'}),
            'month': forms.Select(attrs={'required': 'required'}),
            'year': forms.Select(attrs={'required': 'required'}),
            'source': forms.FileInput(attrs={'required': 'required'}),
        }


class ProcesaCdrForm(forms.Form):

    pass


class FacturaForm(forms.ModelForm):

    class Meta:
        model = models.Factura
        fields = ('compania', 'month', 'year')
        labels = {
            'month': u'Mes', 'year': u'Año', 'compania': u'Compañia',
        }
        widgets = {
            'compania': forms.Select(attrs={'required': 'required'}),
            'month': forms.Select(attrs={'required': 'required'}),
            'year': forms.Select(attrs={'required': 'required'}),
        }
