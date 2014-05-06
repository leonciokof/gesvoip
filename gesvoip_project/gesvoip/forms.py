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
