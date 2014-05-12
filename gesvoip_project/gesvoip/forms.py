# -*- coding: utf-8 -*-

from django import forms

from . import choices, models


class EmailTextInput(forms.widgets.TextInput):

    input_type = 'email'


class NumberTextInput(forms.widgets.TextInput):

    input_type = 'number'


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


class BuscaFacturaForm(forms.Form):

    factura = forms.ModelChoiceField(
        label='Seleccionar factura',
        queryset=models.Factura.objects.all(),
        widget=forms.Select(attrs={'required': 'required'}))


class FeriadoForm(forms.ModelForm):

    class Meta:
        model = models.Feriado
        labels = {'fecha': u'Ingrese fecha'}
        widgets = {
            'fecha': forms.TextInput(
                attrs={'required': 'required', 'autofocus': 'autofocus'}),
        }


class BuscaFeriadoForm(forms.Form):

    feriado = forms.ModelChoiceField(
        label='Seleccionar feriado',
        queryset=models.Feriado.objects.all(),
        widget=forms.Select(attrs={'required': 'required'}))


class NuevaTarifaForm(forms.Form):

    compania = forms.ModelChoiceField(
        queryset=models.Compania.objects.all(),
        widget=forms.Select(attrs={'required': 'required'}))
    fecha_inicio = forms.DateField(
        widget=forms.TextInput(attrs={'required': 'required'}))
    fecha_fin = forms.DateField(
        widget=forms.TextInput(attrs={'required': 'required'}))
    valor_normal = forms.FloatField(
        label='Valor horario normal ($/seg)',
        widget=NumberTextInput(attrs={
            'required': 'required',
            'min': '0.0001',
            'step': '0.0001',
            'placeholder': '0.0001'}))
    valor_reducido = forms.FloatField(
        label='Valor horario reducido ($/seg)',
        widget=NumberTextInput(attrs={
            'required': 'required',
            'min': '0.0001',
            'step': '0.0001',
            'placeholder': '0.0001'}))
    valor_nocturno = forms.FloatField(
        label='Valor horario ncturno ($/seg)',
        widget=NumberTextInput(attrs={
            'required': 'required',
            'min': '0.0001',
            'step': '0.0001',
            'placeholder': '0.0001'}))


class CompaniaFechaForm(forms.Form):

    MONTHS = list(choices.MONTHS)
    MONTHS.insert(0, ('', '---------'))
    YEARS = choices.YEARS
    YEARS.insert(0, ('', '---------'))
    compania = forms.ModelChoiceField(
        queryset=models.Compania.objects.all(),
        widget=forms.Select(attrs={'required': 'required'}))
    month = forms.ChoiceField(
        label='Mes',
        choices=MONTHS,
        widget=forms.Select(attrs={'required': 'required'}))
    year = forms.ChoiceField(
        label='Año',
        choices=YEARS,
        widget=forms.Select(attrs={'required': 'required'}))


class EditaTarifaForm(forms.Form):

    id_ingreso = forms.CharField(widget=forms.HiddenInput())
    valor_normal = forms.FloatField(
        label='Valor horario normal ($/seg)',
        widget=NumberTextInput(attrs={
            'required': 'required',
            'min': '0.0001',
            'step': '0.0001',
            'placeholder': '0.0001'}))
    valor_reducido = forms.FloatField(
        label='Valor horario reducido ($/seg)',
        widget=NumberTextInput(attrs={
            'required': 'required',
            'min': '0.0001',
            'step': '0.0001',
            'placeholder': '0.0001'}))
    valor_nocturno = forms.FloatField(
        label='Valor horario ncturno ($/seg)',
        widget=NumberTextInput(attrs={
            'required': 'required',
            'min': '0.0001',
            'step': '0.0001',
            'placeholder': '0.0001'}))
